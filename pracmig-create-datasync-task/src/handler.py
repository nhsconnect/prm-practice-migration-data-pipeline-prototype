import json
from crhelper import CfnResource
import logging
import os
from urllib.parse import urlparse, parse_qs
from http.client import HTTPConnection


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


helper = CfnResource(
    json_logging=False,
    log_level='DEBUG',
    boto_level='CRITICAL'
)


def handler(event, context):
    helper(event, context)

@helper.create
def create(event, context):
    logger.info("Create request received:\n" + json.dumps(event))

    try:
        AGENT_IP = os.environ['AGENT_IP']
        key = ""
        if event["RequestType"] in ["Create", "Update"]:
            logger.info(f'Requesting Activation Key: http://{AGENT_IP}/?activationRegion=eu-west-2')
            connection = HTTPConnection(AGENT_IP, 80, timeout=2)
            connection.request('GET', "/?activationRegion=eu-west-2")
            response = connection.getresponse()
            key = parse_qs(urlparse(response.getheader("Location")).query)['activationKey'][0]
        # Items stored in helper.Data will be saved 
        # as outputs in your resource in CloudFormation
        helper.Data.update({"ActivationKey": key})
        return "DataSyncActivationKey"
    except Exception as e:
        logger.error(f"Unable to activate agent {e}", exc_info=1)
        raise


@helper.update
def update(event, context):
    logger.info("Update request received:\n" + json.dumps(event))
    return "DataSyncActivationKey"


@helper.delete
def delete(event, context):
    logger.info("Delete request received:\n" + json.dumps(event))
