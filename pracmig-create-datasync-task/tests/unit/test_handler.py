from mock.mock import ANY
from hamcrest import *
from src.handler import handler
from mock import Mock, MagicMock
import json


def test_handler_sends_activation_key_to_cloud_formation_when_creating(monkeypatch):
    activation_key = "KEY_00000"
    response_url = "/custom-resource-response-url"
    stack_id = "arn:aws:cloudformation:eu-west-2:123456789012:stack/mystack-mynestedstack-sggfrhxhum7w/f449b250-b969-11e0-a185-5081d0136786";
    request_id = "test-request-id"
    logical_resource_id = "test-logical-resource-id"
    monkeypatch.setenv("AGENT_IP", "18.170.222.23")
    cf_request_mock = MagicMock()
    cf_call_mock = MagicMock(return_value=Mock(request=cf_request_mock, getresponse=lambda: Mock(status=200, reason="some reason")))
    monkeypatch.setattr("crhelper.utils.HTTPSConnection", cf_call_mock)
    mock_agent_call = Mock(history=["", Mock(url=f"http://mock-redirect/?activationKey={activation_key}")])
    monkeypatch.setattr("requests.get", lambda url, timeout: mock_agent_call)
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

    cf_request_mock.assert_called_with(method="PUT", url=response_url, body=ANY, headers=ANY)
    deserialised_body = json.loads(cf_request_mock.call_args.kwargs["body"])
    assert_that(deserialised_body, has_entry("Status", "SUCCESS"))
    assert_that(deserialised_body, has_entry("StackId", stack_id))
    assert_that(deserialised_body, has_entry("RequestId", request_id))
    assert_that(deserialised_body, has_entry("LogicalResourceId", logical_resource_id))
    assert_that(deserialised_body, has_entry("Data", has_entry("ActivationKey", activation_key)))


def test_handler_sends_activation_key_to_cloud_formation_when_deleting(monkeypatch):
    activation_key = "KEY_00000"
    response_url = "/custom-resource-response-url"
    stack_id = "arn:aws:cloudformation:eu-west-2:123456789012:stack/mystack-mynestedstack-sggfrhxhum7w/f449b250-b969-11e0-a185-5081d0136786";
    request_id = "test-request-id"
    logical_resource_id = "test-logical-resource-id"
    monkeypatch.setenv("AGENT_IP", "18.170.222.23")
    cf_request_mock = MagicMock()
    cf_call_mock = MagicMock(return_value=Mock(request=cf_request_mock, getresponse=lambda: Mock(status=200, reason="some reason")))
    monkeypatch.setattr("crhelper.utils.HTTPSConnection", cf_call_mock)
    mock_agent_call = Mock(history=["", Mock(url=f"http://mock-redirect/?activationKey={activation_key}")])
    monkeypatch.setattr("requests.get", lambda url, timeout: mock_agent_call)
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

    cf_request_mock.assert_called_with(method="PUT", url=response_url, body=ANY, headers=ANY)
    deserialised_body = json.loads(cf_request_mock.call_args.kwargs["body"])
    assert_that(deserialised_body, has_entry("Status", "SUCCESS"))
    assert_that(deserialised_body, has_entry("StackId", stack_id))
    assert_that(deserialised_body, has_entry("RequestId", request_id))
    assert_that(deserialised_body, has_entry("LogicalResourceId", logical_resource_id))
    assert_that(deserialised_body, has_entry("Data", empty()))
