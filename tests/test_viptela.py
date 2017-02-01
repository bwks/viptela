import json

import pytest
import requests
import responses

try:
    import mock
except ImportError:
    from unittest import mock

from viptela.exceptions import LoginTimeoutError, LoginCredentialsError
from viptela.viptela import (
    Viptela,
    parse_http_success,
    parse_http_error,
    Result,
    HTTP_RESPONSE_CODES
)


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


@pytest.fixture
def base_viptela_no_login():
    return Viptela('user', 'pass', 'test', auto_login=False)


class FakeViptela(Viptela):
    """ Override to test urls """
    @staticmethod
    def _get(session, url, headers=None, timeout=10):
        return url


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
    assert http_response_codes == HTTP_RESPONSE_CODES


def test_parse_http_success_returns_result_object():
    resp = parse_http_success(fake_get_test())
    assert isinstance(resp, Result)


def test_parse_http_success_with_no_data_returns_expected_result():
    resp = parse_http_success(fake_get_test())
    assert resp.ok is True
    assert resp.data == {}
    assert resp.status_code == 200
    assert resp.reason == 'Success'


def test_parse_http_success_returns_with_populated_data_dict_returns_list():
    resp = parse_http_success(fake_get_test(body=json.dumps({'data': [{'key': 'value'}]})))
    assert isinstance(resp.data, list)


def test_parse_http_success_returns_json_with_empty_data_key_returns_empty_dict():
    resp = parse_http_success(fake_get_test(body=json.dumps({'data': []})))
    assert isinstance(resp.data, dict)


def test_parse_http_success_with_config_key_returns_expected_result():
    resp = parse_http_success(fake_get_test(body=json.dumps({'config': 'Some Config'})))
    assert resp.ok is True
    assert resp.data == 'Some Config'
    assert resp.status_code == 200
    assert resp.reason == 'Success'


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


# @pytest.mark.skip()
def test_viptela_login_with_invalid_vmanage_host_raises_login_timeout_error():
    with pytest.raises(LoginTimeoutError):
        Viptela('1.1.1.250', 'blah', 'blah')


def test_viptela_instance_attributes(base_viptela_no_login):
    viptela = base_viptela_no_login
    assert viptela.user == 'user'
    assert viptela.user_pass == 'pass'
    assert viptela.vmanage_server == 'test'
    assert viptela.vmanage_server_port == 8443
    assert viptela.verify is False
    assert viptela.disable_warnings is False
    assert viptela.timeout == 10
    assert viptela.auto_login is False
    assert viptela.base_url == 'https://test:8443/dataservice'


def test_method_urls():
    v = FakeViptela('user', 'pass', 'test', auto_login=False)
    assert v.get_banner() == 'https://test:8443/dataservice/settings/configuration/banner'
    assert v.get_device_by_type('vedges') == 'https://test:8443/dataservice/system/device/vedges'
    assert v.get_device_by_type('controllers') == 'https://test:8443/dataservice/system/device/controllers'
    assert v.get_all_devices() == 'https://test:8443/dataservice/device'
    assert v.get_running_config('12345') == 'https://test:8443/dataservice/template/config/running/12345'
    assert v.get_running_config('12345', True) == 'https://test:8443/dataservice/template/config/attached/12345'
    assert v.get_device_maps() == 'https://test:8443/dataservice/group/map/devices'
    assert v.get_arp_table('12345') == 'https://test:8443/dataservice/device/arp?deviceId=12345'
    assert v.get_bgp_summary('12345') == 'https://test:8443/dataservice/device/bgp/summary?deviceId=12345'
    assert v.get_bgp_routes('12345') == 'https://test:8443/dataservice/device/bgp/routes?deviceId=12345'
    assert v.get_bgp_neighbours('12345') == 'https://test:8443/dataservice/device/bgp/neighbors?deviceId=12345'
    assert v.get_ospf_routes('12345') == 'https://test:8443/dataservice/device/ospf/routes?deviceId=12345'
    assert v.get_ospf_neighbours('12345') == 'https://test:8443/dataservice/device/ospf/neighbor?deviceId=12345'
    assert v.get_ospf_database('12345') == 'https://test:8443/dataservice/device/ospf/database?deviceId=12345'
    assert v.get_ospf_database('12345', True) == 'https://test:8443/dataservice/device/ospf/databasesummary?deviceId=12345'
    assert v.get_ospf_interfaces('12345') == 'https://test:8443/dataservice/device/ospf/interface?deviceId=12345'
    assert v.get_transport_connection('12345') == 'https://test:8443/dataservice/device/transport/connection?deviceId=12345'
    assert v.get_tunnel_statistics('12345') == 'https://test:8443/dataservice/device/tunnel/statistics?deviceId=12345'
    assert v.get_omp_peers('12345') == 'https://test:8443/dataservice/device/omp/peers?deviceId=12345'
    assert v.get_omp_peers('12345', True) == 'https://test:8443/dataservice/device/omp/synced/peers?deviceId=12345'
    assert v.get_omp_summary('12345') == 'https://test:8443/dataservice/device/omp/summary?deviceId=12345'

