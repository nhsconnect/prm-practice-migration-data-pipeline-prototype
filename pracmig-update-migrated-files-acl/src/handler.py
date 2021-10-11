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
        logging.error("Error extracting logs: %s", e)
        return {
            'statusCode': 500,
            'body': f'Error putting ACL: { e }'
        }

    master_session = boto3.session.Session()
    s3 = master_session.client('s3')

    try:
        # Use the task to identify source and target locations
        taskARN = os.environ['TASK_ARN']
        destination_bucket_name, destination_path = destination_details(taskARN)
    except Exception as e:
        logging.error("Error getting destination details: %s", e)
        return {
            'statusCode': 500,
            'body': f'Error getting destination details: { e }'
        }

    try:
        for log_event in log_events:
            update_acl(s3, destination_bucket_name, destination_path, log_event)
    except Exception as e:
        logging.error("Error putting ACL: %s", e)
        return {
            'statusCode': 500,
            'body': f'Error putting ACL: { e }'
        }

    return {
        'statusCode': 200
    }


def update_acl(s3, destination_bucket_name, destination_path, log_event):
    file_event = log_event['message']
    regexp = re.compile(r'(\/.*)+\,')
    m = regexp.search(file_event)
    file_path = m.group().rstrip(',')
    key = destination_path + file_path[1:]

    s3.put_object_acl(
        ACL='bucket-owner-full-control',
        Bucket=destination_bucket_name,
        Key=key,
    )


def destination_details(taskARN):
    destination_uri = destination_location_uri(taskARN)

    S3_URI_PREFIX_LEN = 5 # prefix = "s3://"
    destination_uri_path = destination_uri[S3_URI_PREFIX_LEN:]
    destination_segments = destination_uri_path.split('/', 1)
    destination_bucket_name = destination_segments[0]
    destination_root_path = destination_segments[1]
    return destination_bucket_name,destination_root_path


def destination_location_uri(taskARN):
    taskInfo = ds.describe_task(TaskArn=taskARN)
    targetARN = taskInfo['DestinationLocationArn']
    allLocations = ds.list_locations()
    for locations in allLocations['Locations']:
        if locations['LocationArn'] == targetARN:
            destination_location_uri = locations['LocationUri']
    return destination_location_uri


def get_cloud_watch_log_events(event):
    cw_data = event['awslogs']['data']
    compressed_payload = base64.b64decode(cw_data)
    uncompressed_payload = gzip.decompress(compressed_payload)
    payload = json.loads(uncompressed_payload)
    log_events = payload['logEvents']
    return log_events
