import json
import boto3
import logging

def lambda_handler(event, context):
    client = boto3.client('ec2')
    
    response = client.describe_instances(
        Filters=[
            {
                'Name': 'tag:CreatedBy',
                'Values': [
                    'prm-practice-migration-data-pipeline-prototype',
                ]
            },
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running'
                ]
            }
        ],
        DryRun=False,
        MaxResults=50
    )
    reservations = response["Reservations"]

    for reservation in reservations:
        instance_id = reservation["Instances"][0]["InstanceId"] 
        
        response = client.stop_instances(
            InstanceIds=[
                instance_id
            ]
        )
        logging.info(f'Stopped instance: {instance_id}')

    return {
        'statusCode': 200
    }
