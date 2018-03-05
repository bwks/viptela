"""Tests for the parent viptela module."""


import pytest

try:
    import mock
except ImportError:
    from unittest import mock

from viptela.exceptions import LoginTimeoutError
from viptela import constants
from viptela import utils
from viptela import viptela


_MOCK_SESSION = 'mock_session'
_MOCK_BANNER = 'this is a mock banner string'
_MOCK_TEMPLATE_DESC = 'mock template description'
_MOCK_TEMPLATE_NAME = 'mock template'
_TEST_DATA = {'test_data_key': 'test_data_value'}
_TEST_HEADER = {'test_header_key': 'test_header_value'}
_TEST_URL = 'http://test.test'
_TEST_TIMEOUT = 11


class TestViptelaStaticMethods(object):
    """Test the static methods of the Viptela object - these are used for interacting with HTTP
    methods."""

    def setup(self):
        self.session = mock.MagicMock()
        self.session.get = mock.MagicMock
        self.session.post = mock.MagicMock
        self.session.put = mock.MagicMock
        self.session.delete = mock.MagicMock
        self.viptela_device = viptela.Viptela('user', 'pass', 'test', auto_login=False)

    @staticmethod
    def parse_response(session):
        return session

    @mock.patch.object(utils, 'parse_response')
    def test_get_no_headers(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.get(self.session, url=_TEST_URL)
        assert _TEST_URL == return_data.url
        assert constants.STANDARD_JSON_HEADER == return_data.headers
        assert constants.STANDARD_HTTP_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_get_with_headers(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.get(self.session, url=_TEST_URL, headers=_TEST_HEADER,
                                              timeout=_TEST_TIMEOUT)
        assert _TEST_URL == return_data.url
        assert _TEST_HEADER == return_data.headers
        assert _TEST_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_put_no_header_no_data(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.put(self.session, url=_TEST_URL)
        assert _TEST_URL == return_data.url
        assert constants.STANDARD_JSON_HEADER == return_data.headers
        assert {} == return_data.data
        assert constants.STANDARD_HTTP_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_put_with_header_and_data(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.put(self.session, url=_TEST_URL, headers=_TEST_HEADER,
                                              data=_TEST_DATA, timeout=_TEST_TIMEOUT)
        assert _TEST_URL == return_data.url
        assert _TEST_HEADER == return_data.headers
        assert _TEST_DATA == return_data.data
        assert _TEST_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_post_no_header_no_data(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.post(self.session, url=_TEST_URL)
        assert _TEST_URL == return_data.url
        assert constants.STANDARD_JSON_HEADER == return_data.headers
        assert {} == return_data.data
        assert constants.STANDARD_HTTP_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_post_with_header_and_data(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.post(self.session, url=_TEST_URL, headers=_TEST_HEADER,
                                               data=_TEST_DATA, timeout=_TEST_TIMEOUT)
        assert _TEST_URL == return_data.url
        assert _TEST_HEADER == return_data.headers
        assert _TEST_DATA == return_data.data
        assert _TEST_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_delete_no_header_no_data(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.delete(self.session, url=_TEST_URL)
        assert _TEST_URL == return_data.url
        assert constants.STANDARD_JSON_HEADER == return_data.headers
        assert {} == return_data.data
        assert constants.STANDARD_HTTP_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_delete_with_header_and_data(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.delete(self.session, url=_TEST_URL, headers=_TEST_HEADER,
                                               data=_TEST_DATA, timeout=_TEST_TIMEOUT)
        assert _TEST_URL == return_data.url
        assert _TEST_HEADER == return_data.headers
        assert _TEST_DATA == return_data.data
        assert _TEST_TIMEOUT == return_data.timeout


class TestViptelaSetMethods(object):
    """Test set methods of the Viptela API object."""

    def setup(self):
        self.viptela_device = viptela.Viptela('user', 'pass', 'test', auto_login=False)
        self.viptela_device.put = self.mock_http_method
        self.viptela_device.post = self.mock_http_method
        self.viptela_device.delete = self.mock_http_method

    @staticmethod
    def mock_http_method(session, url, data):
        _ = session
        return mock.MagicMock(url=url, data=data)

    def test_set_banner(self):
        banner = 'test banner!'
        return_data = self.viptela_device.set_banner(banner=banner)
        assert 'https://test:8443/dataservice/settings/configuration/banner' == return_data.url
        assert '{"mode": "on", "bannerDetail": "test banner!"}' == return_data.data

    def test_set_template_aaa(self):
        return_data = self.viptela_device.set_template_aaa(data=_MOCK_BANNER)
        assert 'https://test:8443/dataservice/template/feature' == return_data.url
        assert _MOCK_BANNER == return_data.data

    def test_set_template_banner_raises_no_banners(self):
        with pytest.raises(AttributeError) as excinfo:
            self.viptela_device.set_template_banner(template_name=_MOCK_TEMPLATE_NAME,
                                                    template_description=_MOCK_TEMPLATE_DESC)
        assert 'login_banner and/or motd_banner are required.' == str(excinfo.value)

    def test_set_template_banner_raises_bad_models_instance(self):
        with pytest.raises(AttributeError) as excinfo:
            self.viptela_device.set_template_banner(template_name=_MOCK_TEMPLATE_NAME,
                                                    template_description=_MOCK_TEMPLATE_DESC,
                                                    device_models={}, login_banner=_MOCK_BANNER)
        assert 'Device types should be a list' == str(excinfo.value)

    def test_set_template_banner_raises_bad_models(self):
        with pytest.raises(AttributeError) as excinfo:
            self.viptela_device.set_template_banner(template_name=_MOCK_TEMPLATE_NAME,
                                                    template_description=_MOCK_TEMPLATE_DESC,
                                                    device_models=['bad model'],
                                                    login_banner=_MOCK_BANNER)
        assert 'Invalid device type. Valid types are: {0}'.format(
            ', '.join(constants.ALL_DEVICE_TYPES)) == str(excinfo.value)

    def test_set_template_banner(self):
        return_data = self.viptela_device.set_template_banner(
            template_name=_MOCK_TEMPLATE_NAME, template_description=_MOCK_TEMPLATE_DESC,
            device_models='vedge-cloud', login_banner=_MOCK_BANNER, motd_banner=_MOCK_BANNER
        )
        assert 'https://test:8443/dataservice/template/feature' == return_data.url
        assert ('{"templateName": "mock template", "templateDescription": "mock template '
                'description", "templateType": "banner", "templateMinVersion": "15.0.0", '
                '"templateDefinition": {"login": {"vipObjectType": "object", "vipType": '
                '"constant", "vipValue": "this is a mock banner string", "vipVariableName": '
                '"banner_login"}, "motd": {"vipObjectType": "object", "vipType": "constant", '
                '"vipValue": "this is a mock banner string", "vipVariableName": "banner_motd"}}, '
                '"factoryDefault": false, "deviceType": ["vedge-cloud"], "deviceModels": [{"name": '
                '"vedge-cloud", "displayName": "vEdge Cloud", "deviceType": "vedge"}, {"name": '
                '"vedge-100", "displayName": "vEdge 100", "deviceType": "vedge"}, {"name": '
                '"vedge-100-B", "displayName": "vEdge 100 B", "deviceType": "vedge"}, {"name": '
                '"vedge-100-M", "displayName": "vEdge 100 M", "deviceType": "vedge"}, {"name": '
                '"vedge-100-WM", "displayName": "vEdge 100 WM", "deviceType": "vedge"}, {"name": '
                '"vedge-1000", "displayName": "vEdge 1000", "deviceType": "vedge"}, {"name": '
                '"vedge-2000", "displayName": "vEdge 2000", "deviceType": "vedge"}, {"name": '
                '"vmanage", "displayName": "vManage", "deviceType": "vmanage"}, {"name": '
                '"vsmart", "displayName": "vSmart", "deviceType": "vsmart"}]}') == return_data.data

    def test_set_template_logging(self):
        return_data = self.viptela_device.set_template_logging(
            template_name=_MOCK_TEMPLATE_NAME, template_description=_MOCK_TEMPLATE_DESC,
            device_models='vedge-cloud')
        assert 'https://test:8443/dataservice/template/feature' == return_data.url
        assert ('{"templateName": "mock template", "templateDescription": "mock template '
                'description", "templateType": "logging", "templateMinVersion": "15.0.0", '
                '"templateDefinition": {"disk": {"enable": {"vipObjectType": "object", '
                '"vipType": "ignore", "vipValue": "true"}, "file": {"size": {"vipObjectType": '
                '"object", "vipType": "ignore", "vipValue": 10}, "rotate": {"vipObjectType": '
                '"object", "vipType": "ignore", "vipValue": 10}}, "priority": {"vipObjectType": '
                '"object", "vipType": "ignore", "vipValue": "information"}}}, "factoryDefault": '
                'false, "deviceType": ["v", "e", "d", "g", "e", "-", "c", "l", "o", "u", "d"], '
                '"deviceModels": [{"name": "vedge-cloud", "displayName": "vEdge Cloud", '
                '"deviceType": "vedge"}, {"name": "vedge-100", "displayName": "vEdge 100", '
                '"deviceType": "vedge"}, {"name": "vedge-100-B", "displayName": "vEdge 100 B", '
                '"deviceType": "vedge"}, {"name": "vedge-100-M", "displayName": "vEdge 100 M", '
                '"deviceType": "vedge"}, {"name": "vedge-100-WM", "displayName": "vEdge 100 WM", '
                '"deviceType": "vedge"}, {"name": "vedge-1000", "displayName": "vEdge 1000", '
                '"deviceType": "vedge"}, {"name": "vedge-2000", "displayName": "vEdge 2000", '
                '"deviceType": "vedge"}, {"name": "vmanage", "displayName": "vManage", '
                '"deviceType": "vmanage"}, {"name": "vsmart", "displayName": "vSmart", '
                '"deviceType": "vsmart"}]}') == return_data.data

    def test_set_template_omp_bad_device(self):
        with pytest.raises(AttributeError) as excinfo:
            self.viptela_device.set_template_omp(template_name=_MOCK_TEMPLATE_NAME,
                                                 template_description=_MOCK_TEMPLATE_DESC,
                                                 device_type='vmanage')
        assert 'Invalid device type. Valid types are: vedge, vsmart' == str(excinfo.value)

    def test_set_template_omp_vedge(self):
        return_data = self.viptela_device.set_template_omp(
            template_name=_MOCK_TEMPLATE_NAME, template_description=_MOCK_TEMPLATE_DESC,
            device_type='vedge')
        assert 'https://test:8443/dataservice/template/feature' == return_data.url
        assert ('{"templateName": "mock template", "templateDescription": "mock template '
                'description", "templateType": "omp-vedge", "templateMinVersion": "15.0.0", '
                '"templateDefinition": {"graceful-restart": {"vipObjectType": "object", "vipType": '
                '"ignore", "vipValue": "true"}, "send-path-limit": {"vipObjectType": "object", '
                '"vipType": "ignore", "vipValue": 4}, "shutdown": {"vipObjectType": "object", '
                '"vipType": "ignore", "vipValue": "false"}, "timers": {"advertisement-interval": '
                '{"vipObjectType": "object", "vipType": "ignore", "vipValue": 1}, '
                '"graceful-restart-timer": {"vipObjectType": "object", "vipType": "ignore", '
                '"vipValue": 43200}, "holdtime": {"vipObjectType": "object", "vipType": "ignore", '
                '"vipValue": 60}, "eor-timer": {"vipObjectType": "object", "vipType": "ignore", '
                '"vipValue": 300}}, "ecmp-limit": {"vipObjectType": "object", "vipType": "ignore", '
                '"vipValue": 4}, "advertise": {"vipType": "constant", "vipValue": '
                '[{"priority-order": ["protocol", "route"], "protocol": {"vipObjectType": "object",'
                ' "vipType": "constant", "vipValue": "ospf"}, "route": {"vipObjectType": "object",'
                ' "vipType": "constant", "vipValue": "external"}}, {"priority-order": ["protocol"],'
                ' "protocol": {"vipObjectType": "object", "vipType": "constant", "vipValue": '
                '"connected"}}, {"priority-order": ["protocol"], "protocol": {"vipObjectType": '
                '"object", "vipType": "constant", "vipValue": "static"}}], "vipObjectType": "tree",'
                ' "vipPrimaryKey": ["protocol"]}}, "factoryDefault": false, "deviceType": '
                '["vedge-cloud", "vedge-100", "vedge-100-B", "vedge-100-M", "vedge-100-WM", '
                '"vedge-1000", "vedge-2000"], "deviceModels": [{"name": "vedge-cloud", '
                '"displayName": "vEdge Cloud", "deviceType": "vedge"}, {"name": "vedge-100", '
                '"displayName": "vEdge 100", "deviceType": "vedge"}, {"name": "vedge-100-B",'
                ' "displayName": "vEdge 100 B", "deviceType": "vedge"}, {"name": "vedge-100-M", '
                '"displayName": "vEdge 100 M", "deviceType": "vedge"}, {"name": "vedge-100-WM", '
                '"displayName": "vEdge 100 WM", "deviceType": "vedge"}, {"name": "vedge-1000", '
                '"displayName": "vEdge 1000", "deviceType": "vedge"}, {"name": "vedge-2000", '
                '"displayName": "vEdge 2000", "deviceType": "vedge"}]}') == return_data.data

    def test_set_template_omp_vsmart(self):
        return_data = self.viptela_device.set_template_omp(
            template_name=_MOCK_TEMPLATE_NAME, template_description=_MOCK_TEMPLATE_DESC,
            device_type='vsmart')
        assert 'https://test:8443/dataservice/template/feature' == return_data.url
        assert ('{"templateName": "mock template", "templateDescription": "mock template '
                'description", "templateType": "omp-vsmart", "templateMinVersion": "15.0.0",'
                ' "templateDefinition": {"graceful-restart": {"vipObjectType": "object", '
                '"vipType": "ignore", "vipValue": "true"}, "send-path-limit": {"vipObjectType": '
                '"object", "vipType": "ignore", "vipValue": 4}, "shutdown": {"vipObjectType": '
                '"object", "vipType": "ignore", "vipValue": "false"}, "timers": '
                '{"advertisement-interval": {"vipObjectType": "object", "vipType": "ignore", '
                '"vipValue": 1}, "graceful-restart-timer": {"vipObjectType": "object", "vipType": '
                '"ignore", "vipValue": 43200}, "holdtime": {"vipObjectType": "object", "vipType": '
                '"ignore", "vipValue": 60}, "eor-timer": {"vipObjectType": "object", "vipType": '
                '"ignore", "vipValue": 300}}, "send-backup-paths": {"vipObjectType": "object", '
                '"vipType": "ignore", "vipValue": "false"}, "discard-rejected": {"vipObjectType": '
                '"object", "vipType": "ignore", "vipValue": "false"}}, "factoryDefault": false, '
                '"deviceType": ["vsmart"], "deviceModels": ["name", "displayName", '
                '"deviceType"]}') == return_data.data

    def test_set_policy_vsmart(self):
        return_data = self.viptela_device.set_policy_vsmart(
            policy_name=_MOCK_TEMPLATE_NAME, policy_description=_MOCK_TEMPLATE_DESC,
            policy_configuration=_TEST_DATA)
        assert 'https://test:8443/dataservice/template/policy/vsmart' == return_data.url
        assert ('{"policyName": "mock template", "policyDescription": "mock template description", '
                '"policyDefinition": {"test_data_key": "test_data_value"}}') == return_data.data

    def test_set_template_ntp(self):
        return_data = self.viptela_device.set_template_ntp(
            template_name=_MOCK_TEMPLATE_NAME, template_description=_MOCK_TEMPLATE_DESC,
            ntp_servers=[
                {'ipv4_address': 'mock_address_1', 'vpn': 'mock_vpn_1',
                 'version': 'mock_version_1', 'prefer': False},
                {'ipv4_address': 'mock_address_2', 'vpn': 'mock_vpn_2',
                 'version': 'mock_version_2', 'prefer': True}
            ])
        assert 'https://test:8443/dataservice/template/feature' == return_data.url
        assert ('{"templateName": "mock template", "templateDescription": "mock template '
                'description", "templateType": "ntp", "templateMinVersion": "15.0.0", '
                '"templateDefinition": {"keys": {"trusted": {"vipObjectType": "list", "vipType": '
                '"ignore"}}, "server": {"vipObjectType": "tree", "vipType": "constant", "vipValue":'
                ' [{"name": {"vipObjectType": "object", "vipType": "constant", "vipValue": '
                '"mock_address_1"}, "key": {"vipObjectType": "object", "vipType": "ignore"}, "vpn":'
                ' {"vipObjectType": "object", "vipType": "ignore", "vipValue": "mock_vpn_1"}, '
                '"version": {"vipObjectType": "object", "vipType": "ignore", "vipValue": '
                '"mock_version_1"}, "source-interface": {"vipObjectType": "object", "vipType": '
                '"ignore"}, "prefer": {"vipObjectType": "object", "vipType": "constant", '
                '"vipValue": false}, "priority-order": ["name", "key", "vpn", "version", '
                '"source-interface", "prefer"]}, {"name": {"vipObjectType": "object", "vipType": '
                '"constant", "vipValue": "mock_address_2"}, "key": {"vipObjectType": "object", '
                '"vipType": "ignore"}, "vpn": {"vipObjectType": "object", "vipType": "ignore", '
                '"vipValue": "mock_vpn_2"}, "version": {"vipObjectType": "object", "vipType": '
                '"ignore", "vipValue": "mock_version_2"}, "source-interface": {"vipObjectType": '
                '"object", "vipType": "ignore"}, "prefer": {"vipObjectType": "object", "vipType": '
                '"constant", "vipValue": true}, "priority-order": ["name", "key", "vpn", "version",'
                ' "source-interface", "prefer"]}], "vipPrimaryKey": ["name"]}}, "factoryDefault": '
                'false, "deviceType": ["vedge-cloud", "vedge-100", "vedge-100-B", "vedge-100-M", '
                '"vedge-100-WM", "vedge-1000", "vedge-2000", "vmanage", "vsmart"], "deviceModels": '
                '[{"name": "vedge-cloud", "displayName": "vEdge Cloud", "deviceType": "vedge"}, '
                '{"name": "vedge-100", "displayName": "vEdge 100", "deviceType": "vedge"}, {"name":'
                ' "vedge-100-B", "displayName": "vEdge 100 B", "deviceType": "vedge"}, {"name": '
                '"vedge-100-M", "displayName": "vEdge 100 M", "deviceType": "vedge"}, {"name": '
                '"vedge-100-WM", "displayName": "vEdge 100 WM", "deviceType": "vedge"}, {"name": '
                '"vedge-1000", "displayName": "vEdge 1000", "deviceType": "vedge"}, {"name": '
                '"vedge-2000", "displayName": "vEdge 2000", "deviceType": "vedge"}, {"name": '
                '"vmanage", "displayName": "vManage", "deviceType": "vmanage"}, {"name": "vsmart",'
                ' "displayName": "vSmart", "deviceType": "vsmart"}]}') == return_data.data

    def test_set_template_snmpv2(self):
        return_data = self.viptela_device.set_template_snmpv2(
            template_name=_MOCK_TEMPLATE_NAME, template_description=_MOCK_TEMPLATE_DESC,
            snmp_contact='mock_contact', v2_community='mock_community', shutdown=constants.TRUE)
        assert 'https://test:8443/dataservice/template/feature' == return_data.url
        assert ('{"templateName": "mock template", "templateDescription": "mock template '
                'description", "templateType": "snmp", "templateMinVersion": "15.0.0", '
                '"templateDefinition": {"shutdown": {"vipObjectType": "object", "vipType": '
                '"constant", "vipValue": "true"}, "contact": {"vipObjectType": "object", '
                '"vipType": "constant", "vipValue": "mock_contact"}, "name": {"vipObjectType": '
                '"object", "vipType": "variable"}, "location": {"vipObjectType": "object", '
                '"vipType": "variable"}, "view": {"vipType": "constant", "vipValue": [{"name": '
                '{"vipObjectType": "object", "vipType": "constant", "vipValue": "mock_community"}, '
                '"viewMode": "add", "priority-order": ["name"]}], "vipObjectType": "tree", '
                '"vipPrimaryKey": ["name"]}, "trap": {"group": {"vipType": "ignore", "vipValue": '
                '[], "vipObjectType": "tree", "vipPrimaryKey": ["group-name"]}, "target": '
                '{"vipType": "ignore", "vipValue": [], "vipObjectType": "tree", "vipPrimaryKey": '
                '["vpn-id", "ip", "port"]}}}, "factoryDefault": false, "deviceType": '
                '["vedge-cloud", "vedge-100", "vedge-100-B", "vedge-100-M", "vedge-100-WM", '
                '"vedge-1000", "vedge-2000", "vmanage", "vsmart"], "deviceModels": [{"name": '
                '"vedge-cloud", "displayName": "vEdge Cloud", "deviceType": "vedge"}, {"name": '
                '"vedge-100", "displayName": "vEdge 100", "deviceType": "vedge"}, {"name": '
                '"vedge-100-B", "displayName": "vEdge 100 B", "deviceType": "vedge"}, {"name": '
                '"vedge-100-M", "displayName": "vEdge 100 M", "deviceType": "vedge"}, {"name": '
                '"vedge-100-WM", "displayName": "vEdge 100 WM", "deviceType": "vedge"}, {"name": '
                '"vedge-1000", "displayName": "vEdge 1000", "deviceType": "vedge"}, {"name": '
                '"vedge-2000", "displayName": "vEdge 2000", "deviceType": "vedge"}, {"name": '
                '"vmanage", "displayName": "vManage", "deviceType": "vmanage"}, {"name": "vsmart", '
                '"displayName": "vSmart", "deviceType": "vsmart"}]}') == return_data.data

    def test_delete_template_raises(self):
        with pytest.raises(AttributeError) as excinfo:
            self.viptela_device.delete_template()
        assert 'Either template_name or template_id is required' == str(excinfo.value)


class TestViptelaDeleteMethods(object):
    """Test set methods of the Viptela API object."""

    def setup(self):
        self.viptela_device = viptela.Viptela('user', 'pass', 'test', auto_login=False)
        self.viptela_device.put = self.mock_http_method
        self.viptela_device.post = self.mock_http_method
        self.viptela_device.delete = self.mock_http_method
        self.mock_get_template_feature = mock.MagicMock(
                data={'data': [
                    {constants.TEMPLATE_NAME: _MOCK_TEMPLATE_NAME, constants.TEMPLATE_ID: 0},
                    {constants.TEMPLATE_NAME: _MOCK_TEMPLATE_NAME + '1', constants.TEMPLATE_ID: 1},
                    {constants.TEMPLATE_NAME: _MOCK_TEMPLATE_NAME + '2', constants.TEMPLATE_ID: 2}
                ]}
            )
        self.viptela_device.get_template_feature = mock.MagicMock(
            return_value=self.mock_get_template_feature
        )

    @staticmethod
    def mock_http_method(session, url, data=None):
        _ = session
        return mock.MagicMock(url=url, data=data)

    def test_delete_template_raises(self):
        with pytest.raises(AttributeError) as excinfo:
            self.viptela_device.delete_template()
        assert 'Either template_name or template_id is required' == str(excinfo.value)

    def test_delete_template_w_template_id_no_template_name(self):
        return_data = self.viptela_device.delete_template(
            template_name=_MOCK_TEMPLATE_NAME, template_id='1')
        assert 'https://test:8443/dataservice/template/feature/1' == return_data.url

    def test_delete_template_w_no_template_id_template_name(self):
        return_data = self.viptela_device.delete_template(
            template_name=_MOCK_TEMPLATE_NAME,)
        assert 'https://test:8443/dataservice/template/feature/0' == return_data.url




@pytest.fixture
def base_viptela_no_login():
    return viptela.Viptela('user', 'pass', 'test', auto_login=False)


class FakeViptela(viptela.Viptela):
    """ Overriding static methods to test get and set methods."""
    @staticmethod
    def get(session, url, headers=None, timeout=10):
        return url

    @staticmethod
    def put(session, url, headers=None, data=None, timeout=10):
        return url, headers, data

    @staticmethod
    def post(session, url, headers=None, data=None, timeout=10):
        return url, headers, data

    @staticmethod
    def delete(session, url, headers=None, data=None, timeout=10):
        return url, headers, data


def test_viptela_login_with_invalid_vmanage_host_raises_login_timeout_error():
    with pytest.raises(LoginTimeoutError):
        viptela.Viptela('1.1.1.250', 'blah', 'blah', timeout=0.1)


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


def test_get_device_by_type_with_invalid_type_raises_value_error(base_viptela_no_login):
    with pytest.raises(ValueError):
        v = base_viptela_no_login
        v.get_device_by_type('invalid')


def test_get_method_urls():
    v = FakeViptela('user', 'pass', 'test', auto_login=False)
    assert v.get_banner() == 'https://test:8443/dataservice/settings/configuration/banner'
    assert v.get_device_by_type('vedges') == 'https://test:8443/dataservice/system/device/vedges'
    assert v.get_device_by_type('controllers') == ('https://test:8443/dataservice/system/device/'
                                                   'controllers')
    assert v.get_all_devices() == 'https://test:8443/dataservice/device'
    assert v.get_running_config('12345') == ('https://test:8443/dataservice/template/config/'
                                             'running/12345')
    assert v.get_running_config('12345', True) == ('https://test:8443/dataservice/template/config/'
                                                   'attached/12345')
    assert v.get_device_maps() == 'https://test:8443/dataservice/group/map/devices'
    assert v.get_arp_table('12345') == 'https://test:8443/dataservice/device/arp?deviceId=12345'
    assert v.get_bgp_summary('12345') == ('https://test:8443/dataservice/device/bgp/'
                                          'summary?deviceId=12345')
    assert v.get_bgp_routes('12345') == ('https://test:8443/dataservice/device/bgp/'
                                         'routes?deviceId=12345')
    assert v.get_bgp_neighbours('12345') == ('https://test:8443/dataservice/device/bgp/'
                                             'neighbors?deviceId=12345')
    assert v.get_ospf_routes('12345') == ('https://test:8443/dataservice/device/ospf/'
                                          'routes?deviceId=12345')
    assert v.get_ospf_neighbours('12345') == ('https://test:8443/dataservice/device/ospf/'
                                              'neighbor?deviceId=12345')
    assert v.get_ospf_database('12345') == ('https://test:8443/dataservice/device/ospf/'
                                            'database?deviceId=12345')
    assert v.get_ospf_database('12345', True) == ('https://test:8443/dataservice/device/ospf/'
                                                  'databasesummary?deviceId=12345')
    assert v.get_ospf_interfaces('12345') == ('https://test:8443/dataservice/device/ospf/'
                                              'interface?deviceId=12345')
    assert v.get_transport_connection('12345') == ('https://test:8443/dataservice/device/transport/'
                                                   'connection?deviceId=12345')
    assert v.get_tunnel_statistics('12345') == ('https://test:8443/dataservice/device/tunnel/'
                                                'statistics?deviceId=12345')
    assert v.get_omp_peers('12345') == ('https://test:8443/dataservice/device/omp/'
                                        'peers?deviceId=12345')
    assert v.get_omp_peers('12345', True) == ('https://test:8443/dataservice/device/omp/synced/'
                                              'peers?deviceId=12345')
    assert v.get_omp_summary('12345') == ('https://test:8443/dataservice/device/omp/'
                                          'summary?deviceId=12345')
    assert v.get_cellular_modem('12345') == ('https://test:8443/dataservice/device/cellular/'
                                             'modem?deviceId=12345')
    assert v.get_cellular_network('12345') == ('https://test:8443/dataservice/device/cellular/'
                                               'network?deviceId=12345')
    assert v.get_cellular_profiles('12345') == ('https://test:8443/dataservice/device/cellular/'
                                                'profiles?deviceId=12345')
    assert v.get_cellular_radio('12345') == ('https://test:8443/dataservice/device/cellular/'
                                             'radio?deviceId=12345')
    assert v.get_cellular_status('12345') == ('https://test:8443/dataservice/device/cellular/'
                                              'status?deviceId=12345')
    assert v.get_cellular_sessions('12345') == ('https://test:8443/dataservice/device/cellular/'
                                                'sessions?deviceId=12345')
    assert v.get_ipsec_inbound('12345') == ('https://test:8443/dataservice/device/ipsec/'
                                            'inbound?deviceId=12345')
    assert v.get_ipsec_outbound('12345') == ('https://test:8443/dataservice/device/ipsec/'
                                             'outbound?deviceId=12345')
    assert v.get_ipsec_localsa('12345') == ('https://test:8443/dataservice/device/ipsec/'
                                            'localsa?deviceId=12345')
    assert v.get_template_feature() == 'https://test:8443/dataservice/template/feature'
    assert v.get_template_feature('12345') == ('https://test:8443/dataservice/template/feature/object/12345')

