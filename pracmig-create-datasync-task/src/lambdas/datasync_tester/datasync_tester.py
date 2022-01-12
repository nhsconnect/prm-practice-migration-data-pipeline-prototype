import os
from pyNfsClient import (Portmap, Mount, NFSv3, MNT3_OK, NFS_PROGRAM,
                         NFS_V3, NFS3_OK, DATA_SYNC, GUARDED)
from urllib.parse import urlparse
import boto3
import logging
import polling
import uuid
from pyNfsClient import RPC

import socket
from random import randint


def connect(self):
    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.client.settimeout(self.timeout)
    # if we are running as root, use a source port between 500 and 1024 (NFS security options...)
    random_port = None
    try:
        i = 0
        while True:
            try:
                random_port = randint(10500, 101023)
                i += 1
                self.client.bind(('', random_port))
                self.client_port = random_port
                logging.debug("Port %d occupied" % self.client_port)
                break
            except:
                logging.warning(
                    "Socket port binding with %d failed in loop %d, try again." % (random_port, i))
                continue
    except Exception as e:
        logging.error(e)

    self.client.connect((self.host, self.port))
    RPC.connections.append(self)


RPC.connect = connect


REGION = "eu-west-2"


def handler(event, context):
    try:
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        task_arn = event["TaskArn"]
        source_data = "test"

        # object_key = write_test_data_to_source_supplier_bucket(
        #     source_data, task_arn)
        # logging.info(f"Test object written with key: {object_key}")

        object_key = write_test_data_to_source_supplier_nfs(
            source_data, task_arn)
        logging.info(f"Test file written with key: {object_key}")

        transfer_files(task_arn)

        target_data = read_test_data_from_target_supplier_bucket(
            task_arn, object_key)

        if source_data != target_data:
            logging.info(
                f"Data written ({source_data}) does not match data read ({target_data})")
            return {
                "statusCode": 500,
                "body": "Data written does not match data read"
            }

        logging.info("Data written matches data read")
        return {
            "statusCode": 200,
            "body": "Data written matches data read"
        }
    except KeyError as e:
        logging.error(e)
        return {
            "statusCode": 400
        }
    except Exception as e:
        logging.error(e)
        return {
            "statusCode": 500
        }


def extract_name_and_path_from_bucket_uri(location_uri):
    bucket_name_and_path = location_uri.split("//", 1)[1]
    split_bucket_name_and_path = bucket_name_and_path.split('/', 1)
    bucket_name = split_bucket_name_and_path[0]
    path = split_bucket_name_and_path[1]

    return bucket_name, path


def get_bucket_name_and_path(task_arn, location_arn_key):
    datasync_client = boto3.client('datasync', region_name=REGION)
    task = datasync_client.describe_task(
        TaskArn=task_arn
    )

    location_arn = task[location_arn_key]

    location = datasync_client.describe_location_s3(
        LocationArn=location_arn
    )

    bucket_name, path = extract_name_and_path_from_bucket_uri(
        location_uri=location["LocationUri"])

    return bucket_name, path


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


def read_test_data_from_target_supplier_bucket(task_arn, object_key):
    bucket_name, path = get_bucket_name_and_path(
        task_arn, location_arn_key="DestinationLocationArn")
    logging.info(f'Target bucket name: {bucket_name}')
    logging.info(f'Target path: {path}')

    s3_client = boto3.client(
        's3',
        region_name=REGION
    )

    object_path = os.path.join(path, object_key)

    response = s3_client.get_object(Bucket=bucket_name, Key=f"{object_path}")
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
    bucket_name = get_bucket_name_and_path(
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
        "uid": 1000,
        "gid": 1000,
        "aux_gid": list(),
    }

    # portmap initialization
    logging.debug("Portmap connecting...")
    TIMEOUT = 3
    try:
        portmap = Portmap(host, timeout=TIMEOUT)
        portmap.connect()
        logging.debug("...Portmap connected")
    except:
        logging.error("Failed to connect Portmap")
        raise

    # mount initialization
    mnt_port = portmap.getport(Mount.program, Mount.program_version)
    logging.debug(f"Mount connecting on port {mnt_port}...")
    mount = Mount(host=host, port=mnt_port, timeout=TIMEOUT, auth=auth)
    mount.connect()
    logging.debug("...Mount connected")

    # do mount
    logging.debug(f"Mounting path {mount_path}...")
    mnt_res = mount.mnt(mount_path, auth)
    nfs3 = None
    logging.debug(f"Mount result: {mnt_res['status']}")
    if mnt_res["status"] == MNT3_OK:
        logging.debug("Mounted OK")
        root_fh = mnt_res["mountinfo"]["fhandle"]
        try:
            nfs_port = portmap.getport(NFS_PROGRAM, NFS_V3)
            # nfs actions
            logging.debug(f"NFSv3 connecting on port {nfs_port}")
            nfs3 = NFSv3(host, nfs_port, TIMEOUT, auth=auth)
            nfs3.connect()
            logging.debug("...NFSv3 connected ")
            logging.debug("Performing NFSv3 lookup...")
            create_res = nfs3.create(root_fh, file_name, create_mode=GUARDED)
            logging.debug(f"...NFSv3 create result: {create_res['status']}")
            if create_res["status"] == NFS3_OK:
                fh = create_res["resok"]["obj"]["handle"]["data"]
                logging.debug(f"Writing file content to file...")
                write_res = nfs3.write(fh, offset=0, count=len(data), content=data,
                                       stable_how=DATA_SYNC, auth=auth)
                logging.debug("...File content written")
                if write_res["status"] != NFS3_OK:
                    raise Exception(
                        f"Write failed with status: {write_res['status']}")
            else:
                raise Exception(
                    f"Create failed with status: {create_res['status']}")
            return file_name
        finally:
            if nfs3:
                nfs3.disconnect()
            mount.umnt()
            mount.disconnect()
            portmap.disconnect()
    else:
        mount.disconnect()
        portmap.disconnect()
        raise Exception(f"Mount failed with status {mnt_res['status']}")
