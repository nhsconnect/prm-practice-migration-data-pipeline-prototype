import json
import cfnresponse
import os
from urllib.parse import urlparse, parse_qs
import requests
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def handler(event, context):
    logging.info("REQUEST RECEIVED:\n" + json.dumps(event))
    try:
        AGENT_IP = os.environ['AGENT_IP']
        key = {}
        if event["RequestType"] in ["Create", "Update"]:
            logger.info(f'Requesting Activation Key: http://{AGENT_IP}/?activationRegion=eu-west-2')
            res = requests.get(f'http://{AGENT_IP}/?activationRegion=eu-west-2', timeout=2)
            res.raise_for_status()
            key = parse_qs(urlparse(res.history[1].url).query)['activationKey'][0]
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {"ActivationKey": key})
    except requests.exceptions.RequestException as e:
        logger.error(f"Unable to activate agent", exc_info=1)
        raise
