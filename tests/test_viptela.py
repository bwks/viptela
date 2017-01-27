import json

import pytest
import requests
import responses

try:
    import mock
except ImportError:
    from unittest import mock

from viptela.exceptions import LoginTimeoutError, LoginCredentialsError
from viptela.viptela import parse_http_success, parse_http_error, Result


@pytest.fixture
def fake_get_test(status=200, body=None):
    if body is None:
        body = json.dumps({})
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, 'http://test.com',
                 body=body, status=status,
                 content_type='application/json')
        resp = requests.get('http://test.com')
    return resp


def test_parse_http_success_returns_result_object():
    resp = parse_http_success(fake_get_test())
    assert isinstance(resp, Result)


def test_parse_http_success_with_key_error_returns_expected_result():
    resp = parse_http_success(fake_get_test())
    assert resp.ok is True
    assert resp.data == {}
    assert resp.status_code == 200
    assert resp.reason == 'No data received from device'


def test_parse_http_success_returns_with_populated_data_dict_returns_list():
    resp = parse_http_success(fake_get_test(body=json.dumps({'data': [{'key': 'value'}]})))
    assert isinstance(resp.data, list)


def test_parse_http_success_returns_json_with_empty_data_key_returns_empty_dict():
    resp = parse_http_success(fake_get_test(body=json.dumps({'data': []})))
    assert isinstance(resp.data, dict)


def test_parse_http_error_returns_expected_result():
    error_data = {
        'error': {
            'details': 'error_details',
            'message': 'error_message'
        }
    }
    resp = parse_http_error(fake_get_test(status=400, body=json.dumps(error_data)))
    assert resp.ok is False
    assert resp.data == {}
    assert resp.status_code == 400
    assert resp.reason == 'error_details'
    assert resp.error == 'error_message'
