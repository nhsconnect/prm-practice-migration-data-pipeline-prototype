from http.client import HTTPException
from mock.mock import ANY
from hamcrest import *
from src.handler import handler
from mock import Mock, MagicMock
import json


def test_handler_sends_activation_key_to_cloud_formation_when_creating(monkeypatch):
    activation_key = "KEY_00000"
    response_url = "/custom-resource-response-url"
    stack_id = "arn:aws:cloudformation:eu-west-2:123456789012:stack/mystack-mynestedstack-sggfrhxhum7w/f449b250-b969-11e0-a185-5081d0136786"
    request_id = "test-request-id"
    logical_resource_id = "test-logical-resource-id"
    monkeypatch.setenv("AGENT_IP", "35.179.77.230")
    cf_request_mock = MagicMock()
    cf_call_mock = MagicMock(return_value=Mock(
        request=cf_request_mock, getresponse=lambda: Mock(status=200, reason="some reason")))
    monkeypatch.setattr("crhelper.utils.HTTPSConnection", cf_call_mock)
    mock_key_request_conn = Mock(getresponse=lambda: Mock(
        getheader=lambda _: f"http://mock-redirect/?activationKey={activation_key}"))
    monkeypatch.setattr(
        "src.handler.HTTPConnection",
        lambda host, port, timeout: mock_key_request_conn)
    event = {
        "RequestType": "Create",
        "ResponseURL": f"https://aws-cloud-formation-host.com{response_url}",
        "StackId": stack_id,
        "RequestId": request_id,
        "LogicalResourceId": logical_resource_id
    }
    context = Mock(
        log_stream_name="blah",
        get_remaining_time_in_millis=lambda: 5000
    )

    handler(event, context)

    cf_request_mock.assert_called_with(
        method="PUT", url=response_url, body=ANY, headers=ANY)
    deserialised_body = json.loads(cf_request_mock.call_args.kwargs["body"])
    assert_that(deserialised_body, has_entry("Status", "SUCCESS"))
    assert_that(deserialised_body, has_entry("StackId", stack_id))
    assert_that(deserialised_body, has_entry("RequestId", request_id))
    assert_that(
        deserialised_body, has_entry("LogicalResourceId", logical_resource_id))
    assert_that(
        deserialised_body,
        has_entry("Data", has_entry("ActivationKey", activation_key)))


def test_handler_retries_activation_call(monkeypatch):
    monkeypatch.setenv("AGENT_IP", "35.179.77.230")
    cf_request_mock = MagicMock()
    cf_call_mock = MagicMock(return_value=Mock(
        request=cf_request_mock, getresponse=lambda: Mock(status=200, reason="some reason")))
    monkeypatch.setattr("crhelper.utils.HTTPSConnection", cf_call_mock)
    mock_activation_key_request = MagicMock(side_effect=[HTTPException, None])
    mock_key_request_conn = Mock(
        getresponse=lambda: Mock(
            getheader=lambda _: "http://mock-redirect/?activationKey=KEY_00000"),
        request=mock_activation_key_request)
    monkeypatch.setattr(
        "src.handler.HTTPConnection",
        lambda host, port, timeout: mock_key_request_conn)
    event = {
        "RequestType": "Create",
        "ResponseURL": f"https://aws-cloud-formation-host.com/custom-resource-response-url",
        "StackId": "arn:aws:cloudformation:eu-west-2:123456789012:stack/mystack-mynestedstack-sggfrhxhum7w/f449b250-b969-11e0-a185-5081d0136786",
        "RequestId": "test-request-id",
        "LogicalResourceId": "test-logical-resource-id"
    }
    context = Mock(
        log_stream_name="blah",
        get_remaining_time_in_millis=lambda: 5000
    )

    handler(event, context)

    assert_that(mock_activation_key_request.call_args_list, has_length(2))
    cf_request_mock.assert_called_with(
        method="PUT", url=ANY, body=ANY, headers=ANY)
    deserialised_body = json.loads(cf_request_mock.call_args.kwargs["body"])
    assert_that(deserialised_body, has_entry("Status", "SUCCESS"))


def test_handler_sends_failure_notification_to_cf_when_agent_ip_not_set(monkeypatch):
    cf_request_mock = MagicMock()
    cf_call_mock = MagicMock(return_value=Mock(
        request=cf_request_mock, getresponse=lambda: Mock(status=200, reason="some reason")))
    monkeypatch.setattr("crhelper.utils.HTTPSConnection", cf_call_mock)
    event = {
        "RequestType": "Create",
        "ResponseURL": f"https://aws-cloud-formation-host.com/custom-resource-response-url",
        "StackId": "arn:aws:cloudformation:eu-west-2:123456789012:stack/mystack-mynestedstack-sggfrhxhum7w/f449b250-b969-11e0-a185-5081d0136786",
        "RequestId": "test-request-id",
        "LogicalResourceId": "test-logical-resource-id"
    }
    context = Mock(
        log_stream_name="blah",
        get_remaining_time_in_millis=lambda: 5000
    )

    handler(event, context)

    cf_request_mock.assert_called_with(
        method="PUT", url=ANY, body=ANY, headers=ANY)
    deserialised_body = json.loads(cf_request_mock.call_args.kwargs["body"])
    assert_that(deserialised_body, has_entry("Status", "FAILED"))


def test_handler_sends_activation_key_to_cloud_formation_when_deleting(monkeypatch):
    response_url = "/custom-resource-response-url"
    stack_id = "arn:aws:cloudformation:eu-west-2:123456789012:stack/mystack-mynestedstack-sggfrhxhum7w/f449b250-b969-11e0-a185-5081d0136786"
    request_id = "test-request-id"
    logical_resource_id = "test-logical-resource-id"
    cf_request_mock = MagicMock()
    cf_call_mock = MagicMock(return_value=Mock(
        request=cf_request_mock, getresponse=lambda: Mock(status=200, reason="some reason")))
    monkeypatch.setattr("crhelper.utils.HTTPSConnection", cf_call_mock)
    event = {
        "RequestType": "Delete",
        "ResponseURL": f"https://aws-cloud-formation-host.com{response_url}",
        "StackId": stack_id,
        "RequestId": request_id,
        "LogicalResourceId": logical_resource_id
    }
    context = Mock(
        log_stream_name="blah",
        get_remaining_time_in_millis=lambda: 5000
    )

    handler(event, context)

    cf_request_mock.assert_called_with(
        method="PUT", url=response_url, body=ANY, headers=ANY)
    deserialised_body = json.loads(cf_request_mock.call_args.kwargs["body"])
    assert_that(deserialised_body, has_entry("Status", "SUCCESS"))
    assert_that(deserialised_body, has_entry("StackId", stack_id))
    assert_that(deserialised_body, has_entry("RequestId", request_id))
    assert_that(
        deserialised_body, has_entry("LogicalResourceId", logical_resource_id))
    assert_that(deserialised_body, has_entry("Data", empty()))
