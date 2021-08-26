import boto3
import logging
import polling
from botocore.exceptions import ClientError
import uuid

REGION = "eu-west-2"


def test_migrator(event, context):
    try:
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        task_arn = event["TaskArn"]
        target_bucket_role_arn = event["TargetBucketAccessRoleArn"]
        source_data = "test"

        object_key = write_test_data_to_source_supplier_bucket(source_data, task_arn)
        logging.info(f"Test object written with key: {object_key}")

        transfer_files(task_arn)

        target_data = read_test_data_from_target_supplier_bucket(task_arn, target_bucket_role_arn, object_key)

        if source_data != target_data:
            return {
                "statusCode": 500,
                "body": f"Data written ({source_data}) does not match data read ({target_data})"
            }
        return {
            "statusCode": 200,
            "body": f"Data written matches data read"
        }
    except ClientError as e:
        logging.error(e)
        return {
            "statusCode": 500
        }
    except KeyError as e:
        logging.error(e)
        return {
            "statusCode": 400
        }


def extract_name_from_bucket_uri(location_uri):
    location_uri = location_uri.split("//")
    bucket_name = location_uri[1].replace("/", "")

    return bucket_name


def assume_role(role_arn):
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="AssumeRoleTargetAccount"
    )
    credentials = assumed_role_object['Credentials']

    return credentials


def retrieve_bucket_name(task_arn, location_arn_key):
    datasync_client = boto3.client('datasync', region_name=REGION)
    task = datasync_client.describe_task(
        TaskArn=task_arn
    )

    location_arn = task[location_arn_key]

    location = datasync_client.describe_location_s3(
        LocationArn=location_arn
    )

    bucket_name = extract_name_from_bucket_uri(location_uri=location["LocationUri"])

    return bucket_name


def read_test_data_from_target_supplier_bucket(task_arn, role_arn, object_key):
    bucket_name = retrieve_bucket_name(task_arn, location_arn_key="DestinationLocationArn")
    logging.info(f'Target bucket name: {bucket_name}')

    credentials = assume_role(role_arn)
    logging.info(f'Assumed role: {role_arn}')

    s3_client = boto3.client(
        's3',
        region_name=REGION,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    response = s3_client.get_object(Bucket=bucket_name, Key=f"{object_key}")
    logging.info(response)
    data = response['Body'].read().decode("utf-8")
    return data


def transfer_files(task_arn):
    datasync_client, task_execution_response = start_transfer(task_arn)

    def check_success(response):
        return response["Status"] == "SUCCESS"
    polling.poll(lambda: datasync_client.describe_task_execution(TaskExecutionArn=task_execution_response["TaskExecutionArn"]),
                        check_success=check_success, step=10, poll_forever=True)


def start_transfer(task_arn):
    datasync_client = boto3.client('datasync', region_name=REGION)
    task_execution_response = datasync_client.start_task_execution(TaskArn=task_arn)
    return datasync_client, task_execution_response


def write_test_data_to_source_supplier_bucket(data, task_arn):
    bucket_name = retrieve_bucket_name(task_arn, location_arn_key="SourceLocationArn")

    s3_client = boto3.client('s3', region_name=REGION)
    object_key = f"{uuid.uuid4()}.txt"
    s3_client.put_object(Body=bytearray(data, encoding="utf-8"), Bucket=bucket_name, Key=object_key)
    return object_key