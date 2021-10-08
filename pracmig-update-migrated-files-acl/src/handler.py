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
    master_session = boto3.session.Session()
    s3 = master_session.client('s3')

    log_events = get_cloud_watch_log_events(event)

    # Use the task to identify source and target locations
    taskARN = os.environ['TASK_ARN']
    taskInfo = ds.describe_task(TaskArn=taskARN)
    targetARN = taskInfo['DestinationLocationArn']
    allLocations = ds.list_locations()
    for locs in allLocations['Locations']:
        if locs['LocationArn'] == targetARN:
            full_target = locs['LocationUri'][5:]
            targetElements = full_target.split('/', 1)
            target_loc = targetElements[0]
            prefix = targetElements[1]

    try:
        for log_event in log_events:
            fileEvent = log_event['message']
            regexp = re.compile(r'(\/.*)+\,')
            m = regexp.search(fileEvent)
            fileLoc = m.group().rstrip(',')
            key = prefix + fileLoc[1:]

            s3.put_object_acl(
                ACL='bucket-owner-full-control',
                Bucket=target_loc,
                Key=key,
            )
    except Exception as e:
        logging.error("Error putting ACL: %s", e)
        return {
            'statusCode': 500
        }

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def get_cloud_watch_log_events(event):
    cw_data = event['awslogs']['data']
    compressed_payload = base64.b64decode(cw_data)
    uncompressed_payload = gzip.decompress(compressed_payload)
    payload = json.loads(uncompressed_payload)
    log_events = payload['logEvents']
    return log_events
