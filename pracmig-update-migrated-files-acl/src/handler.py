import gzip
import json
import base64
import os
import re
import boto3
import logging

s3 = boto3.resource('s3')
ds = boto3.client('datasync')


def lambda_handler(event, context):
    try:
        log_events = get_cloud_watch_log_events(event)
    except Exception as e:
        return {
            'statusCode': 400,
            'body': f'Error updating object ACL: { e }'
        }

    master_session = boto3.session.Session()
    s3 = master_session.client('s3')

    try:
        # Use the task to identify source and target locations
        task_arn = get_task_arn()
        destination_bucket_name, destination_path = destination_details(task_arn)

        for log_event in log_events:
            update_acl(s3, destination_bucket_name, destination_path, log_event)

        return {
            'statusCode': 200
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error updating object ACL: {e}'
        }


def get_task_arn():
    try:
        task_arn = os.environ['TASK_ARN']
        return task_arn
    except Exception as e:
        logging.error("'TASK_ARN' environment variable is not set")
        raise Exception('Lambda is incorrectly configured')


def update_acl(s3, destination_bucket_name, destination_path, log_event):
    try:
        file_event = log_event['message']
        regexp = re.compile(r'(\/.*)+\,')
        m = regexp.search(file_event)
        file_path = m.group().rstrip(',')
        key = destination_path + file_path[1:]
    except Exception as e:
        logging.error("Unable to extract file path from log event: %s", e)
        raise Exception("Invalid log event received")

    try:
        s3.put_object_acl(
            ACL='bucket-owner-full-control',
            Bucket=destination_bucket_name,
            Key=key,
        )
    except Exception as e:
        logging.error(
            f"Updating ACL failed for object with key '{key}'"
            + f" in bucket '{destination_bucket_name}': %s", e)
        raise Exception("Lambda is incorrectly configured")


def destination_details(task_arn):
    try:
        destination_uri = get_destination_location_uri(task_arn)

        S3_URI_PREFIX_LEN = 5 # prefix = "s3://"
        destination_uri_path = destination_uri[S3_URI_PREFIX_LEN:]
        destination_segments = destination_uri_path.split('/', 1)
        destination_bucket_name = destination_segments[0]
        destination_root_path = destination_segments[1]
        return destination_bucket_name,destination_root_path
    except Exception as e:
        logging.error(f"Unable to extract destination details from task: '{task_arn}'. Error: {e}")
        raise Exception('Lambda is incorrectly configured')


def get_destination_location_uri(task_arn):
    taskInfo = ds.describe_task(TaskArn=task_arn)
    destination_location_arn = taskInfo['DestinationLocationArn']
    allLocations = ds.list_locations()
    for locations in allLocations['Locations']:
        if locations['LocationArn'] == destination_location_arn:
            destination_location_uri = locations['LocationUri']
    return destination_location_uri


def get_cloud_watch_log_events(event):
    try:
        cw_data = event['awslogs']['data']
        compressed_payload = base64.b64decode(cw_data)
        uncompressed_payload = gzip.decompress(compressed_payload)
        payload = json.loads(uncompressed_payload)
        log_events = payload['logEvents']
        return log_events
    except Exception as e:
        logging.error("Unable to extract log events: %s", e)
        raise Exception("Invalid data supplied")
