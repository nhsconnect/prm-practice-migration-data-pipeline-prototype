import boto3
import logging
import polling
from botocore.exceptions import ClientError
import uuid
from pyNfsClient import (Portmap, Mount, NFSv3, MNT3_OK, NFS_PROGRAM,
                         NFS_V3, NFS3_OK, DATA_SYNC)
from urllib.parse import urlparse

REGION = "eu-west-2"


def handler(event, context):
    try:
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        task_arn = event["TaskArn"]
        target_bucket_role_arn = event["TargetBucketAccessRoleArn"]
        source_data = "test"

        # object_key = write_test_data_to_source_supplier_bucket(
        #     source_data, task_arn)
        # logging.info(f"Test object written with key: {object_key}")

        object_key = write_test_data_to_source_supplier_nfs(
            source_data, task_arn)
        logging.info(f"Test file written with key: {object_key}")

        transfer_files(task_arn)

        target_data = read_test_data_from_target_supplier_bucket(
            task_arn, target_bucket_role_arn, object_key)

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

    bucket_name = extract_name_from_bucket_uri(
        location_uri=location["LocationUri"])

    return bucket_name


def retrieve_nfs_server_uri(task_arn, location_arn_key):
    datasync_client = boto3.client('datasync', region_name=REGION)
    task = datasync_client.describe_task(
        TaskArn=task_arn
    )

    location_arn = task[location_arn_key]

    location = datasync_client.describe_location_nfs(
        LocationArn=location_arn
    )

    return location["LocationUri"]


def read_test_data_from_target_supplier_bucket(task_arn, role_arn, object_key):
    bucket_name = retrieve_bucket_name(
        task_arn, location_arn_key="DestinationLocationArn")
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
    task_execution_response = datasync_client.start_task_execution(
        TaskArn=task_arn)
    return datasync_client, task_execution_response


def write_test_data_to_source_supplier_bucket(data, task_arn):
    bucket_name = retrieve_bucket_name(
        task_arn, location_arn_key="SourceLocationArn")

    s3_client = boto3.client('s3', region_name=REGION)
    object_key = f"{uuid.uuid4()}.txt"
    s3_client.put_object(Body=bytearray(
        data, encoding="utf-8"), Bucket=bucket_name, Key=object_key)
    return object_key


def write_test_data_to_source_supplier_nfs(data, task_arn):
    nfs_server_uri = retrieve_nfs_server_uri(
        task_arn, location_arn_key="SourceLocationArn")

    parsed_uri = urlparse(nfs_server_uri)
    host = parsed_uri.hostname
    mount_path = parsed_uri.path

    file_name = f"{uuid.uuid4()}.txt"
    auth = {
        "flavor": 1,
        "machine_name": "host1",
        "uid": 0,
        "gid": 0,
        "aux_gid": list(),
    }

    # portmap initialization
    TIMEOUT = 3600
    portmap = Portmap(host, timeout=TIMEOUT)
    portmap.connect()

    # mount initialization
    mnt_port = portmap.getport(Mount.program, Mount.program_version)
    mount = Mount(host=host, port=mnt_port, timeout=TIMEOUT, auth=auth)
    mount.connect()

    # do mount
    mnt_res = mount.mnt(mount_path, auth)
    nfs3 = None
    if mnt_res["status"] == MNT3_OK:
        root_fh = mnt_res["mountinfo"]["fhandle"]
        try:
            nfs_port = portmap.getport(NFS_PROGRAM, NFS_V3)
            # nfs actions
            nfs3 = NFSv3(host, nfs_port, TIMEOUT, auth=auth)
            nfs3.connect()
            lookup_res = nfs3.lookup(root_fh, file_name, auth)
            if lookup_res["status"] == NFS3_OK:
                fh = lookup_res["resok"]["object"]["data"]
                write_res = nfs3.write(fh, offset=0, count=11, content=data,
                                       stable_how=DATA_SYNC, auth=auth)
                if write_res["status"] == NFS3_OK:
                    raise ClientError("NFS Write failed", "NFS Write")
            else:
                raise ClientError("NFS Lookup failed", "NFS Lookup")
            return file_name
        finally:
            if nfs3:
                nfs3.disconnect()
            mount.umnt(mount_path)
            mount.disconnect()
            portmap.disconnect()
    else:
        mount.disconnect()
        portmap.disconnect()
