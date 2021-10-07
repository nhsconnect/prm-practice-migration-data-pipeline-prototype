import os
import sys

import boto3
import pytest
from moto import mock_datasync, mock_s3
from moto.core import set_initial_no_auth_action_count

from src.handler import lambda_handler
from tests.unit.extensions import get_canned_acl

LOG_DATA_GZIP_BASE64_ENCODED = "H4sIAAAAAAAAADWQSU/DMBCF/0rkc0O9L71VECoOwKEVlypCbjKJLLLJdjdV/e84LMd5b5bvzQ31EIJtYXedAK3Q03q3/nwtttv1pkALNJ4H8ElmVCmlFVeYkSR3Y7vx43FKztKew7K20YbrUP1a2+jB9slL4leONUjciAokIVRoCjlcoMoxVaRmpjmYGleag0yz4XgIlXdTdOPw7LoIPqDVHk3eVr1r8wgh5ifwrnFQ543rIKDy52JxgiHOvTfk6hlXMs4pZ0ZyIzWWXGshCBNKaqIp4UZwjYVhOkXCVGpJGWFcscQQXXpItH3KRiQ1ilEqOZFi8f+otH7/9r57eSzK7OMPJpthsuUM+BAvcZHx7HBNFbqX92+m9ifbYgEAAA=="

@pytest.fixture
def fixture(monkeypatch):
    monkeypatch.setattr('moto.s3.models.get_canned_acl', get_canned_acl)

@set_initial_no_auth_action_count(sys.maxsize)
def test_handler_sets_object_acl(monkeypatch, fixture):
    with mock_datasync(), mock_s3():
        DESTINATION_BUCKET_NAME = 'dest-bucket'
        TRANSFERRED_OBJECT_KEY = 'test.txt'
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=DESTINATION_BUCKET_NAME, CreateBucketConfiguration={
            'LocationConstraint': 'eu-west-2'
        })
        s3.put_object(Body='test', Bucket=DESTINATION_BUCKET_NAME, Key=TRANSFERRED_OBJECT_KEY)
        original_object_acl = s3.get_object_acl(Bucket=DESTINATION_BUCKET_NAME, Key=TRANSFERRED_OBJECT_KEY)
        task_arn = create_task(f'arn:aws:s3:::{DESTINATION_BUCKET_NAME}/')
        monkeypatch.setenv('TASK_ARN', task_arn)

        log_events_payload = {
            "awslogs": {
                "data": LOG_DATA_GZIP_BASE64_ENCODED
            }
        }
        lambda_handler(log_events_payload, {})
        
        object_acl = s3.get_object_acl(Bucket=DESTINATION_BUCKET_NAME, Key=TRANSFERRED_OBJECT_KEY)
        assert len(original_object_acl['Grants']) == 0
        assert len(object_acl['Grants']) == 1


def create_task(dest_bucket_arn):
    ds = boto3.client('datasync')
    s3_config = {
        'BucketAccessRoleArn': ''
    }
    source_loc_arn = ds.create_location_s3(S3BucketArn='arn:aws:s3:::source-bucket', S3Config=s3_config)['LocationArn']
    dest_loc_arn = ds.create_location_s3(S3BucketArn=dest_bucket_arn, S3Config=s3_config)['LocationArn']
    task = ds.create_task(SourceLocationArn=source_loc_arn, DestinationLocationArn=dest_loc_arn)
    task_arn = task['TaskArn']
    return task_arn
