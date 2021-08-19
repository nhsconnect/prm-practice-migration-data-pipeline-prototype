import boto3
import logging
import polling
from botocore.exceptions import ClientError

REGION = "eu-west-2"

def testMigrator(event, context):

    try:
        source_data = "test"
        write_test_data_to_source_supplier_bucket(source_data)

        transfer_files()

        target_data = read_test_data_from_target_supplier_bucket()

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

def read_test_data_from_target_supplier_bucket():
    s3_client = boto3.client('s3', region_name=REGION)
    response = s3_client.get_object(Bucket="pracmig-target-supplier-test-bucket", Key="test.txt")
    logging.info(response)
    data = response['Body'].read().decode("utf-8")
    return data

def transfer_files():
    datasync_client, task_execution_response = start_transfer()

    def check_success(response):
        return response["Status"] == "SUCCESS"
    polling.poll(lambda: datasync_client.describe_task_execution(TaskExecutionArn=task_execution_response["TaskExecutionArn"]),
                        check_success=check_success, step=10, poll_forever=True)

def start_transfer():
    datasync_client = boto3.client('datasync', region_name=REGION)
    task_execution_response = datasync_client.start_task_execution(TaskArn="arn:aws:datasync:eu-west-2:327778747031:task/task-0ff150ad6e48c1d28")
    return datasync_client,task_execution_response

def write_test_data_to_source_supplier_bucket(data):
    s3_client = boto3.client('s3', region_name=REGION)
    s3_client.put_object(Body=bytearray(data, encoding="utf-8"), Bucket="pracmig-source-supplier-test-bucket", Key="test.txt")