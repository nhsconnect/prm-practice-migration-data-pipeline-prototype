from http.client import HTTPException
from mock.mock import ANY
from hamcrest import *
from lambdas.agent_activator.agent_activator import handler
from mock import Mock, MagicMock
import json
import pytest

CUSTOM_RESPONSE_PATH = "/custom-resource-response-url"


@pytest.fixture
def cf_request_mock(monkeypatch):
    request_mock = MagicMock()
    cf_call_mock = MagicMock(return_value=Mock(
        request=request_mock, getresponse=lambda: Mock(status=200, reason="some reason")))
    monkeypatch.setattr("crhelper.utils.HTTPSConnection", cf_call_mock)
    return request_mock


@pytest.fixture
def lambda_context():
    return Mock(
        log_stream_name="blah",
        get_remaining_time_in_millis=lambda: 5000
    )


@pytest.fixture
def create_event():
    return {
        "RequestType": "Create",
        "ResponseURL": f"https://aws-cloud-formation-host.com{CUSTOM_RESPONSE_PATH}",
        "StackId": "arn:aws:cloudformation:eu-west-2:123456789012:stack/mystack-mynestedstack-sggfrhxhum7w/f449b250-b969-11e0-a185-5081d0136786",
        "RequestId": "test-request-id",
        "LogicalResourceId": "test-logical-resource-id"
    }


@pytest.fixture
def delete_event():
    return {
        "RequestType": "Delete",
        "ResponseURL": f"https://aws-cloud-formation-host.com{CUSTOM_RESPONSE_PATH}",
        "StackId": "arn:aws:cloudformation:eu-west-2:123456789012:stack/mystack-mynestedstack-sggfrhxhum7w/f449b250-b969-11e0-a185-5081d0136786",
        "RequestId": "test-request-id",
        "LogicalResourceId": "test-logical-resource-id"
    }


def test_handler_sends_activation_key_to_cloud_formation_when_creating(
        monkeypatch, cf_request_mock, create_event, lambda_context):
    activation_key = "KEY_00000"
    monkeypatch.setenv("AGENT_IP", "35.179.77.230")
    mock_key_request_conn = Mock(getresponse=lambda: Mock(
        getheader=lambda _: f"http://mock-redirect/?activationKey={activation_key}"))
    monkeypatch.setattr(
        "lambdas.agent_activator.agent_activator.HTTPConnection",
        lambda host, port, timeout: mock_key_request_conn)

    handler(create_event, lambda_context)

    cf_request_mock.assert_called_with(
        method="PUT", url=CUSTOM_RESPONSE_PATH, body=ANY, headers=ANY)
    deserialised_body = json.loads(cf_request_mock.call_args.kwargs["body"])
    assert_that(deserialised_body, has_entry("Status", "SUCCESS"))
    assert_that(deserialised_body, has_entry(
        "StackId", create_event['StackId']))
    assert_that(deserialised_body, has_entry(
        "RequestId", create_event['RequestId']))
    assert_that(
        deserialised_body,
        has_entry("LogicalResourceId", create_event["LogicalResourceId"]))
    assert_that(
        deserialised_body,
        has_entry("Data", has_entry("ActivationKey", activation_key)))


def test_handler_retries_activation_call(
        monkeypatch, cf_request_mock, create_event, lambda_context):
    monkeypatch.setenv("AGENT_IP", "35.179.77.230")
    mock_activation_key_request = MagicMock(side_effect=[HTTPException, None])
    mock_key_request_conn = Mock(
        getresponse=lambda: Mock(
            getheader=lambda _: "http://mock-redirect/?activationKey=KEY_00000"),
        request=mock_activation_key_request)
    monkeypatch.setattr(
        "lambdas.agent_activator.agent_activator.HTTPConnection",
        lambda host, port, timeout: mock_key_request_conn)

    handler(create_event, lambda_context)

    assert_that(mock_activation_key_request.call_args_list, has_length(2))
    cf_request_mock.assert_called_with(
        method="PUT", url=ANY, body=ANY, headers=ANY)
    deserialised_body = json.loads(cf_request_mock.call_args.kwargs["body"])
    assert_that(deserialised_body, has_entry("Status", "SUCCESS"))


def test_handler_sends_failure_notification_to_cf_when_agent_ip_not_set(
        cf_request_mock, create_event, lambda_context):

    handler(create_event, lambda_context)

    cf_request_mock.assert_called_with(
        method="PUT", url=ANY, body=ANY, headers=ANY)
    deserialised_body = json.loads(cf_request_mock.call_args.kwargs["body"])
    assert_that(deserialised_body, has_entry("Status", "FAILED"))


def test_handler_sends_activation_key_to_cloud_formation_when_deleting(
        cf_request_mock, delete_event, lambda_context):

    handler(delete_event, lambda_context)

    cf_request_mock.assert_called_with(
        method="PUT", url=CUSTOM_RESPONSE_PATH, body=ANY, headers=ANY)
    deserialised_body = json.loads(cf_request_mock.call_args.kwargs["body"])
    assert_that(deserialised_body, has_entry("Status", "SUCCESS"))
    assert_that(
        deserialised_body,
        has_entry("StackId", delete_event["StackId"]))
    assert_that(
        deserialised_body,
        has_entry("RequestId", delete_event["RequestId"]))
    assert_that(
        deserialised_body,
        has_entry("LogicalResourceId", delete_event["LogicalResourceId"]))
    assert_that(deserialised_body, has_entry("Data", empty()))
