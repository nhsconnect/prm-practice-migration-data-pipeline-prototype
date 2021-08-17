import boto3
import logging
import polling
from botocore.exceptions import ClientError

REGION = "eu-west-2"

def testMigrator(event, context):

    try:
        s3_client = boto3.client('s3', region_name=REGION)
        s3_client.put_object(Body=bytearray("test", encoding="utf-8"), Bucket="pracmig-source-supplier-test-bucket", Key="test.txt")
    except ClientError as e:
        logging.error(e)
        return False

    try:
        datasync_client = boto3.client('datasync', region_name=REGION)
        task_execution_response = datasync_client.start_task_execution(TaskArn="arn:aws:datasync:eu-west-2:327778747031:task/task-0ff150ad6e48c1d28")
    except ClientError as e:
        logging.error(e)
        return False

    def check_success(response):
        return response["Status"] == "SUCCESS"
    polling.poll(lambda: datasync_client.describe_task_execution(TaskExecutionArn=task_execution_response["TaskExecutionArn"]),
                 check_success=check_success, step=10, poll_forever=True)

    try:
        s3_client = boto3.client('s3', region_name=REGION)
        response = s3_client.get_object(Bucket="pracmig-target-supplier-test-bucket", Key="test.txt")
        logging.info(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True