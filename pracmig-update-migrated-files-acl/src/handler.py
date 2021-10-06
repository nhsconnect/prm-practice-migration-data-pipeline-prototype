import gzip
import json
import base64
import re
import boto3
import logging

s3 = boto3.resource('s3')
ds = boto3.client('datasync')
task_id = '<task-id-here>'

def lambda_handler(event, context):

    master_session = boto3.session.Session()
    s3 = master_session.client('s3')

    # Capture and convert the cloudwatch logs into text
    log_events = get_cloud_watch_log_events(event)

    logging.info(log_events)

    # Use the task to identify source and target locations
    taskARN = get_task_arn(task_id)
    taskInfo = ds.describe_task(TaskArn=taskARN)
    sourceARN = taskInfo['SourceLocationArn']
    targetARN = taskInfo['DestinationLocationArn']
    allLocations = ds.list_locations()
    for locs in allLocations['Locations']:
        if locs['LocationArn'] == sourceARN:
            source_loc = locs['LocationUri'].rstrip('/')
        if locs['LocationArn'] == targetARN:
            full_target = locs['LocationUri'][5:]
            targetElements = full_target.split('/',1)
            target_loc = targetElements[0]
            prefix = targetElements[1]
    
    try:
        for log_event in log_events:
            fileEvent = log_event['message']
            regexp = re.compile(r'(\/.*)+\,')
            m = regexp.search(fileEvent)
            fileLoc = m.group().rstrip('\,')
            source = source_loc+fileLoc
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

def get_task_arn(datasync_task_id):
    allTasks = ds.list_tasks()
    for tasks in allTasks['Tasks']:
        if re.search(r'.*\/(.*)',tasks['TaskArn']).group(1) == datasync_task_id:
            taskARN = tasks['TaskArn']
    return taskARN

def get_cloud_watch_log_events(event):
    cw_data = event['awslogs']['data']
    compressed_payload = base64.b64decode(cw_data)
    uncompressed_payload = gzip.decompress(compressed_payload)
    payload = json.loads(uncompressed_payload)
    log_events = payload['logEvents']
    return log_events