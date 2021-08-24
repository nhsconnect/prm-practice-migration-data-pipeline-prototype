import boto3
import logging
import polling
from botocore.exceptions import ClientError

REGION = "eu-west-2"
TASK_ARN = "arn:aws:datasync:eu-west-2:327778747031:task/task-077b1497521e705ea"


def test_migrator(event, context):

    try:
        source_data = "test"
        write_test_data_to_source_supplier_bucket(source_data, TASK_ARN)

        transfer_files(TASK_ARN)

        target_data = read_test_data_from_target_supplier_bucket(TASK_ARN)

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


def extract_name_from_bucket_uri(location_uri):
    location_uri = location_uri.split("//")
    bucket_name = location_uri[1].replace("/", "")

    return bucket_name


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


def read_test_data_from_target_supplier_bucket(task_arn):
    bucket_name = retrieve_bucket_name(task_arn, location_arn_key="DestinationLocationArn")
    s3_client = boto3.client('s3', region_name=REGION)
    response = s3_client.get_object(Bucket=bucket_name, Key="test.txt")
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
    s3_client.put_object(Body=bytearray(data, encoding="utf-8"), Bucket=bucket_name, Key="test.txt")