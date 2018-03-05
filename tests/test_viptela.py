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


_MOCK_BANNER = 'this is a mock banner string'
_MOCK_DATA = {'test_data_key': 'test_data_value'}
_MOCK_HEADER = {'test_header_key': 'test_header_value'}
_MOCK_ID = 'mock_id'
_MOCK_SESSION = 'mock_session'
_MOCK_TEMPLATE_DESC = 'mock template description'
_MOCK_TEMPLATE_NAME = 'mock template'
_MOCK_TIMEOUT = 11
_MOCK_URL = 'http://test.test'


def _mock_http_method(session, url, data=None):
    _ = session
    return mock.MagicMock(url=url, data=data)


class TestViptelaLogin(object):

    def setup(self):
        self.viptela_device = viptela.Viptela('user', 'pass', 'test', auto_login=False)

    def test_viptela_login_with_invalid_vmanage_host_raises_login_timeout_error(self):
        with pytest.raises(LoginTimeoutError) as excinfo:
            viptela.Viptela('mock_user', '', 'mock_device', timeout=0.01)
        assert 'Could not connect to mock_device' == str(excinfo.value)

    def test_viptela_instance_attributes(self):
        assert self.viptela_device.user == 'user'
        assert self.viptela_device.user_pass == 'pass'
        assert self.viptela_device.vmanage_server == 'test'
        assert self.viptela_device.vmanage_server_port == 8443
        assert self.viptela_device.verify is False
        assert self.viptela_device.disable_warnings is False
        assert self.viptela_device.timeout == 10
        assert self.viptela_device.auto_login is False
        assert self.viptela_device.base_url == 'https://test:8443/dataservice'


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
        return_data = self.viptela_device.get(self.session, url=_MOCK_URL)
        assert _MOCK_URL == return_data.url
        assert constants.STANDARD_JSON_HEADER == return_data.headers
        assert constants.STANDARD_HTTP_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_get_with_headers(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.get(self.session, url=_MOCK_URL, headers=_MOCK_HEADER,
                                              timeout=_MOCK_TIMEOUT)
        assert _MOCK_URL == return_data.url
        assert _MOCK_HEADER == return_data.headers
        assert _MOCK_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_put_no_header_no_data(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.put(self.session, url=_MOCK_URL)
        assert _MOCK_URL == return_data.url
        assert constants.STANDARD_JSON_HEADER == return_data.headers
        assert {} == return_data.data
        assert constants.STANDARD_HTTP_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_put_with_header_and_data(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.put(self.session, url=_MOCK_URL, headers=_MOCK_HEADER,
                                              data=_MOCK_DATA, timeout=_MOCK_TIMEOUT)
        assert _MOCK_URL == return_data.url
        assert _MOCK_HEADER == return_data.headers
        assert _MOCK_DATA == return_data.data
        assert _MOCK_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_post_no_header_no_data(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.post(self.session, url=_MOCK_URL)
        assert _MOCK_URL == return_data.url
        assert constants.STANDARD_JSON_HEADER == return_data.headers
        assert {} == return_data.data
        assert constants.STANDARD_HTTP_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_post_with_header_and_data(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.post(self.session, url=_MOCK_URL, headers=_MOCK_HEADER,
                                               data=_MOCK_DATA, timeout=_MOCK_TIMEOUT)
        assert _MOCK_URL == return_data.url
        assert _MOCK_HEADER == return_data.headers
        assert _MOCK_DATA == return_data.data
        assert _MOCK_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_delete_no_header_no_data(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.delete(self.session, url=_MOCK_URL)
        assert _MOCK_URL == return_data.url
        assert constants.STANDARD_JSON_HEADER == return_data.headers
        assert {} == return_data.data
        assert constants.STANDARD_HTTP_TIMEOUT == return_data.timeout

    @mock.patch.object(utils, 'parse_response')
    def test_delete_with_header_and_data(self, mock_parse_response):
        mock_parse_response.side_effect = self.parse_response
        return_data = self.viptela_device.delete(self.session, url=_MOCK_URL, headers=_MOCK_HEADER,
                                               data=_MOCK_DATA, timeout=_MOCK_TIMEOUT)
        assert _MOCK_URL == return_data.url
        assert _MOCK_HEADER == return_data.headers
        assert _MOCK_DATA == return_data.data
        assert _MOCK_TIMEOUT == return_data.timeout


class TestViptelaSetMethods(object):
    """Test set methods of the Viptela API object."""

    def setup(self):
        self.viptela_device = viptela.Viptela('user', 'pass', 'test', auto_login=False)
        self.viptela_device.put = _mock_http_method
        self.viptela_device.post = _mock_http_method
        self.viptela_device.delete = _mock_http_method

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
            policy_configuration=_MOCK_DATA)
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
        self.viptela_device.delete = _mock_http_method
        self.viptela_device.get = _mock_http_method
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


class TestGetMethods(object):
    
    def setup(self):
        self.viptela_device = viptela.Viptela('user', 'pass', 'test', auto_login=False)
        self.viptela_device.get = _mock_http_method

    def test_get_banner(self):
        return_data = self.viptela_device.get_banner()
        assert return_data.url == 'https://test:8443/dataservice/settings/configuration/banner'

    def test_get_device_by_type_vedges(self):
        return_data = self.viptela_device.get_device_by_type('vedges')
        assert return_data.url == 'https://test:8443/dataservice/system/device/vedges'

    def test_get_device_by_type_vcontrollers(self):
        return_data = self.viptela_device.get_device_by_type('controllers')
        assert return_data.url == 'https://test:8443/dataservice/system/device/controllers'

    def test_get_device_by_type_raises_value_error(self):
        with pytest.raises(ValueError) as excinfo:
            self.viptela_device.get_device_by_type('bad_device')
        assert 'Invalid device type: bad_device' == str(excinfo.value)

    def test_get_all_devices(self):
        return_data = self.viptela_device.get_all_devices()
        assert return_data.url == 'https://test:8443/dataservice/device'

    def test_get_running_config(self):
        return_data = self.viptela_device.get_running_config(_MOCK_ID)
        assert return_data.url == 'https://test:8443/dataservice/template/config/running/mock_id'

    def test_get_running_config_attached(self):
        return_data = self.viptela_device.get_running_config(_MOCK_ID, True)
        assert return_data.url == 'https://test:8443/dataservice/template/config/attached/mock_id'

    def test_get_device_maps(self):
        return_data = self.viptela_device.get_device_maps()
        assert return_data.url == 'https://test:8443/dataservice/group/map/devices'

    def test_get_arp_table(self):
        return_data = self.viptela_device.get_arp_table(_MOCK_ID)
        assert return_data.url == 'https://test:8443/dataservice/device/arp?deviceId=mock_id'

    def test_get_bgp_summary(self):
        return_data = self.viptela_device.get_bgp_summary(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/bgp/summary?deviceId=mock_id'
        )

    def test_get_bgp_routes(self):
        return_data = self.viptela_device.get_bgp_routes(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/bgp/routes?deviceId=mock_id'
        )

    def test_get_bgp_neighbors(self):
        return_data = self.viptela_device.get_bgp_neighbors(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/bgp/neighbors?deviceId=mock_id'
        )

    def test_get_ospf_routes(self):
        return_data = self.viptela_device.get_ospf_routes(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/ospf/routes?deviceId=mock_id'
        )

    def test_get_ospf_neighbors(self):
        return_data = self.viptela_device.get_ospf_neighbors(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/ospf/neighbor?deviceId=mock_id'
        )

    def test_get_ospf_database(self):
        return_data = self.viptela_device.get_ospf_database(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/ospf/database?deviceId=mock_id'
        )

    def test_get_ospf_database_summary(self):
        return_data = self.viptela_device.get_ospf_database(_MOCK_ID, True)
        assert return_data.url == (
            'https://test:8443/dataservice/device/ospf/databasesummary?deviceId=mock_id'
        )

    def test_get_ospf_interfaces(self):
        return_data = self.viptela_device.get_ospf_interfaces(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/ospf/interface?deviceId=mock_id'
        )

    def test_get_transport_connection(self):
        return_data = self.viptela_device.get_transport_connection(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/transport/connection?deviceId=mock_id'
        )

    def test_get_tunnel_statistics(self):
        return_data = self.viptela_device.get_tunnel_statistics(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/tunnel/statistics?deviceId=mock_id'
        )

    def test_get_omp_peers(self):
        return_data = self.viptela_device.get_omp_peers(_MOCK_ID)
        assert return_data.url == 'https://test:8443/dataservice/device/omp/peers?deviceId=mock_id'

    def test_get_omp_peers_from_vmanage(self):
        return_data = self.viptela_device.get_omp_peers(_MOCK_ID, True)
        assert return_data.url == (
            'https://test:8443/dataservice/device/omp/synced/peers?deviceId=mock_id'
        )

    def test_get_omp_summary(self):
        return_data = self.viptela_device.get_omp_summary(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/omp/summary?deviceId=mock_id'
        )

    def test_get_cellular_modem(self):
        return_data = self.viptela_device.get_cellular_modem(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/cellular/modem?deviceId=mock_id'
        )

    def test_get_cellular_network(self):
        return_data = self.viptela_device.get_cellular_network(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/cellular/network?deviceId=mock_id'
        )

    def test_get_cellular_profiles(self):
        return_data = self.viptela_device.get_cellular_profiles(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/cellular/profiles?deviceId=mock_id'
        )

    def test_get_cellular_radio(self):
        return_data = self.viptela_device.get_cellular_radio(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/cellular/radio?deviceId=mock_id'
        )

    def test_get_cellular_status(self):
        return_data = self.viptela_device.get_cellular_status(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/cellular/status?deviceId=mock_id'
        )

    def test_get_cellular_sessions(self):
        return_data = self.viptela_device.get_cellular_sessions(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/cellular/sessions?deviceId=mock_id'
        )

    def test_get_ipsec_inbound(self):
        return_data = self.viptela_device.get_ipsec_inbound(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/ipsec/inbound?deviceId=mock_id'
        )

    def test_get_ipsec_outbound(self):
        return_data = self.viptela_device.get_ipsec_outbound(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/ipsec/outbound?deviceId=mock_id'
        )

    def test_get_ipsec_localsa(self):
        return_data = self.viptela_device.get_ipsec_localsa(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/device/ipsec/localsa?deviceId=mock_id'
        )

    def test_get_template_feature(self):
        return_data = self.viptela_device.get_template_feature()
        assert return_data.url == 'https://test:8443/dataservice/template/feature'

    def test_get_template_feature_template_id(self):
        return_data = self.viptela_device.get_template_feature(_MOCK_ID)
        assert return_data.url == (
            'https://test:8443/dataservice/template/feature/object/mock_id'
        )
