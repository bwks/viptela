"""Tests for the utils module."""


import json
import logging
import mock
import requests
import responses
import pytest

from viptela import constants, utils
# Minor difference between Python2 and Python3
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError



@responses.activate
def fake_get_test(status=200, body=None):
    if body is None:
        body = json.dumps({})
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, 'http://test.com',
                 body=body, status=status,
                 content_type='application/json')
        resp = requests.get('http://test.com')
    return resp


@responses.activate
def fake_post_test(status=200, body=None):
    if body is None:
        body = json.dumps({})
    with responses.RequestsMock() as rsps:
        rsps.add(responses.POST, 'http://test.com',
                 body=body, status=status,
                 content_type='application/json')
        resp = requests.post('http://test.com')
    return resp


def test_http_response_codes_dict_has_expected_key_value_pairs():
    http_response_codes = {
        200: 'Success',
        400: 'Bad Request',
        403: 'Forbidden',
        404: 'API Not found',
        406: 'Not Acceptable Response',
        415: 'Unsupported Media Type',
        500: 'Internal Server Error'
    }
    assert http_response_codes == constants.HTTP_RESPONSE_CODES


def test_parse_http_success_returns_result_object():
    resp = utils.parse_http_success(fake_get_test())
    assert isinstance(resp, utils.Result)


def test_parse_http_success_post_returns_result_object():
    resp = utils.parse_http_success(fake_post_test())
    assert isinstance(resp, utils.Result)


def test_parse_http_success_post():
    data = {'data': [{'key': 'value'}]}
    resp = utils.parse_http_success(fake_post_test(body=json.dumps(data)))
    assert resp.data == data


def test_parse_http_success_post_bad_json():
    data = 'bad json'
    resp = utils.parse_http_success(fake_post_test(body=data))
    assert resp.data == dict()


def test_parse_http_success_with_no_data_returns_expected_result():
    resp = utils.parse_http_success(fake_get_test())
    assert resp.ok is True
    assert resp.data == {}
    assert resp.status_code == 200
    assert resp.reason == 'Success'


def test_parse_http_success_returns_with_populated_data_dict_returns_list():
    resp = utils.parse_http_success(fake_get_test(body=json.dumps({'data': [{'key': 'value'}]})))
    assert isinstance(resp.data, list)


def test_parse_http_success_returns_json_with_empty_data_key_returns_empty_dict():
    resp = utils.parse_http_success(fake_get_test(body=json.dumps({'data': []})))
    assert isinstance(resp.data, dict)


def test_parse_http_success_with_config_key_returns_expected_result():
    resp = utils.parse_http_success(fake_get_test(body=json.dumps({'config': 'Some Config'})))
    assert resp.ok is True
    assert resp.data == 'Some Config'
    assert resp.status_code == 200
    assert resp.reason == 'Success'


def test_parse_http_success_with_template_definition_key_returns_expected_result():
    resp = utils.parse_http_success(fake_get_test(body=json.dumps({'templateDefinition': 'Some Template'})))
    assert resp.ok is True
    assert resp.data == 'Some Template'
    assert resp.status_code == 200
    assert resp.reason == 'Success'


def test_parse_http_error_returns_expected_result():
    error_data = {
        'error': {
            'details': 'error_details',
            'message': 'error_message'
        }
    }
    resp = utils.parse_http_error(fake_get_test(status=400, body=json.dumps(error_data)))
    assert resp.ok is False
    assert resp.data == {}
    assert resp.status_code == 400
    assert resp.reason == 'error_details'
    assert resp.error == 'error_message'


def test_parse_http_error_bad_error_data():
    error_data = 'bad json'
    resp = utils.parse_http_error(fake_get_test(status=400, body=error_data))
    assert resp.error.__repr__() == "JSONDecodeError('Expecting value: line 1 column 1 (char 0)',)"


@mock.patch.object(utils, 'parse_http_success')
def test_parse_response_success(mock_parse_success):
    resp = fake_get_test(status=200)
    mock_return_string = 'mock string'
    mock_parse_success.return_value = mock_return_string
    assert utils.parse_response(resp) == mock_return_string


@mock.patch.object(utils, 'parse_http_error')
def test_parse_response_error(mock_parse_success):
    resp = fake_get_test(status=400)
    mock_return_string = 'mock string'
    mock_parse_success.return_value = mock_return_string
    assert utils.parse_response(resp) == mock_return_string


def test_check_post_response_no_error():
    response = mock.Mock(error=False)
    checked_response = utils.check_post_response(response)
    assert response == checked_response


def test_check_post_response_error_no_raise(caplog):
    # Capture log messages at debug level
    caplog.set_level(logging.DEBUG)
    response = mock.Mock(error=True, reason='mock reason')
    checked_response = utils.check_post_response(response)
    assert response == checked_response
    assert caplog.records[0].message == 'Failure in POST operation: mock reason.'


def test_check_post_response_error_raise_exception(caplog):
    # Capture log messages at debug level
    caplog.set_level(logging.DEBUG)
    response = mock.Mock(error=True, reason='mock reason')
    with pytest.raises(Exception) as excinfo:
        checked_response = utils.check_post_response(response, raise_error=True)
        assert response == checked_response
    assert caplog.records[0].message == 'Failure in POST operation: mock reason.'
    assert str(excinfo.value) == 'Failure in POST operation.'
