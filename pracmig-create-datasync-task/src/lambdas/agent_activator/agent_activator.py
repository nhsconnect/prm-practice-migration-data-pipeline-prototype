import json
from crhelper import CfnResource
import logging
import os
from urllib.parse import urlparse, parse_qs
from http.client import HTTPConnection
from time import sleep

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


helper = CfnResource(
    json_logging=False,
    log_level='DEBUG',
    boto_level='CRITICAL'
)


def handler(event, context):
    helper(event, context)


TIMEOUT_IN_SECONDS = 3


@helper.create
def create(event, context):
    logger.info("Create request received:\n" + json.dumps(event))

    try:
        agent_ip = os.environ['AGENT_IP']
        key = None
        while key is None:
            try:
                connection = HTTPConnection(
                    agent_ip, 80, timeout=TIMEOUT_IN_SECONDS)
                logger.info(
                    f'Requesting Activation Key: http://{agent_ip}/?activationRegion=eu-west-2')
                connection.request('GET', "/?activationRegion=eu-west-2")
                response = connection.getresponse()
                key = parse_qs(urlparse(
                    response.getheader("Location")).query)["activationKey"][0]
            except Exception as e:
                logger.warning(f"Connection problem: {e}", exc_info=True)
                sleep(2)
        logger.info(f"KEY IS: {key}")
        helper.Data.update({"ActivationKey": key})
    except Exception as e:
        logger.error(f"Unable to activate agent {e}", exc_info=True)
        raise


@helper.update
def update(event, context):
    logger.info("Update request received:\n" + json.dumps(event))


@helper.delete
def delete(event, context):
    logger.info("Delete request received:\n" + json.dumps(event))
