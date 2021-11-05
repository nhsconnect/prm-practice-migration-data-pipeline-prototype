import os
import sys

import boto3
import pytest
from moto.core import set_initial_no_auth_action_count
import urllib
from src.handler import handler
from mock import Mock, MagicMock
import cfnresponse


def test_handler_returns_activation_key(monkeypatch):
    monkeypatch.setenv('AGENT_IP', '18.170.222.23')
    cf_mock = Mock()
    mock_agent_call = Mock(history=['', Mock(url='http://mock-redirect/?activationKey=KEY_00000')])
    monkeypatch.setattr('cfnresponse.send', cf_mock)
    monkeypatch.setattr('requests.get', lambda url: mock_agent_call)
    event = {
        "RequestType": "Create",
        'ResponseURL': 'https://'
    }
    context = {
        "log_stream_name": "blah"
    }
    handler(event, context)
    cf_mock.assert_called_with(event, context, 'SUCCESS', 'KEY_00000', 'ok')
