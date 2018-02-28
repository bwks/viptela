"""Base API class and functions used by the API."""


import json
import requests

from collections import namedtuple
from requests.exceptions import ConnectionError

from viptela.constants import DEVICE_MODEL_MAP, ALL_DEVICE_TYPES, ALL_DEVICE_MODELS, \
    HTTP_SUCCESS_CODES, HTTP_ERROR_CODES, HTTP_RESPONSE_CODES
from . import constants, utils
from . exceptions import LoginCredentialsError, LoginTimeoutError


# Minor difference between Python2 and Python3
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

# parse_response will return a namedtuple object
Result = namedtuple('Result', [
    'ok', 'status_code', 'error', 'reason', 'data', 'response'
])


def parse_http_success(response):
    """
    HTTP 2XX responses
    :param response: requests response object
    :return: namedtuple result object
    """
    if response.request.method in ['GET']:
        reason = constants.HTTP_RESPONSE_CODES[response.status_code]
        error = ''
        if response.json().get(constants.DATA):
            json_response = response.json()[constants.DATA]
        elif response.json().get(constants.CONFIG):
            json_response = response.json()[constants.CONFIG]
        elif response.json().get(constants.TEMPLATE_DEFINITION):
            json_response = response.json()[constants.TEMPLATE_DEFINITION]
        else:
            json_response = dict()
            reason = constants.HTTP_RESPONSE_CODES[response.status_code]
            error = 'No data received from device'
    else:
        try:
            json_response = json.loads(response.text)
        except JSONDecodeError:
            json_response = dict()
        reason = constants.HTTP_RESPONSE_CODES[response.status_code]
        error = ''

    result = Result(
        ok=response.ok,
        status_code=response.status_code,
        reason=reason,
        error=error,
        data=json_response,
        response=response,
    )
    return result


def parse_http_error(response):
    """
    HTTP 4XX and 5XX responses
    :param response: requests response object
    :return: namedtuple result object
    """
    try:
        json_response = dict()
        reason = response.json()[constants.ERROR]['details']
        error = response.json()[constants.ERROR]['message']
    except ValueError as e:
        json_response = dict()
        reason = constants.HTTP_RESPONSE_CODES[response.status_code]
        error = e

    result = Result(
        ok=response.ok,
        status_code=response.status_code,
        reason=reason,
        error=error,
        data=json_response,
        response=response,
    )
    return result


def parse_response(response):
    """
    Parse a request response object
    :param response: requests response object
    :return: namedtuple result object
    """
    if response.status_code in constants.HTTP_SUCCESS_CODES:
        return parse_http_success(response)

    elif response.status_code in constants.HTTP_ERROR_CODES:
        return parse_http_error(response)


def find_feature_template(session, template_name):
    """
    Find a feature template ID by template name.
    """
    all_templates = session.get_template_feature()

    for i in all_templates.data[constants.DATA]:
        if i[constants.TEMPLATE_NAME] == template_name:
            return i[constants.TEMPLATE_ID]
    raise ValueError('Template not found')


def vip_object(vip_object_type='object', vip_type='ignore', vip_value=None,
               vip_variable_name=None, vip_primary_key=None):
    """
    VIP objects are used as configuration elements
    Build a vip object
    """
    vip = {
        'vipObjectType': vip_object_type,
        'vipType': vip_type,
    }

    if vip_value is not None:
        vip.update({'vipValue': vip_value})

    if vip_variable_name is not None:
        vip.update({'vipVariableName': vip_variable_name})

    if vip_primary_key is not None:
        vip.update({'vipPrimaryKey': vip_primary_key})

    return vip


class Viptela(object):
    """
    Class for use with Viptela vManage API.
    """
    @staticmethod
    def get(session, url, headers=None, timeout=10):
        """
        Perform a HTTP get
        :param session: requests session
        :param url: url to get
        :param headers: HTTP headers
        :param timeout: Timeout for request response
        :return:
        """
        if headers is None:
            headers = constants.STANDARD_JSON_HEADER

        return parse_response(session.get(url=url, headers=headers, timeout=timeout))

    @staticmethod
    def put(session, url, headers=None, data=None, timeout=10):
        """
        Perform a HTTP put
        :param session: requests session
        :param url: url to get
        :param headers: HTTP headers
        :param data: Data payload
        :param timeout: Timeout for request response
        :return:
        """
        if headers is None:
            # add default headers for put
            headers = constants.STANDARD_JSON_HEADER

        if data is None:
            data = dict()

        return parse_response(session.put(url=url, headers=headers, data=data, timeout=timeout))

    @staticmethod
    def post(session, url, headers=None, data=None, timeout=10):
        """
        Perform a HTTP post
        :param session: requests session
        :param url: url to post
        :param headers: HTTP headers
        :param data: Data payload
        :param timeout: Timeout for request response
        :return:
        """
        if headers is None:
            # add default headers for post
            headers = constants.STANDARD_JSON_HEADER

        if data is None:
            data = dict()

        return parse_response(session.post(url=url, headers=headers, data=data, timeout=timeout))

    @staticmethod
    def delete(session, url, headers=None, data=None, timeout=10):
        """
        Perform a HTTP delete
        :param session: requests session
        :param url: url to delete
        :param headers: HTTP headers
        :param data: Data payload
        :param timeout: Timeout for request response
        :return:
        """
        if headers is None:
            # add default headers for delete
            headers = constants.STANDARD_JSON_HEADER

        if data is None:
            data = dict()

        return parse_response(session.delete(url=url, headers=headers, data=data, timeout=timeout))

    def __init__(self, user, user_pass, vmanage_server, vmanage_server_port=8443,
                 verify=False, disable_warnings=False, timeout=10, auto_login=True):
        """
        Init method for Viptela class
        :param user: API user name
        :param user_pass: API user password
        :param vmanage_server: vManage server IP address or Hostname
        :param vmanage_server_port: vManage API port
        :param verify: Verify HTTPs certificate verification
        :param disable_warnings: Disable console warnings if ssl cert invalid
        :param timeout: Timeout for request response
        :param auto_login: Automatically login to vManage server
        """
        self.user = user
        self.user_pass = user_pass
        self.vmanage_server = vmanage_server
        self.vmanage_server_port = vmanage_server_port
        self.verify = verify
        self.timeout = timeout
        self.disable_warnings = disable_warnings

        if self.disable_warnings:
            requests.packages.urllib3.disable_warnings()

        self.auto_login = auto_login

        self.base_url = 'https://{0}:{1}/dataservice'.format(
            self.vmanage_server,
            self.vmanage_server_port
        )

        self.session = requests.session()
        if not self.verify:
            self.session.verify = self.verify

        # login
        if self.auto_login:
            self.login_result = self.login()

    def login(self):
        """
        Login to vManage server
        :return: Result named tuple
        """
        try:
            login_result = self.post(
                session=self.session,
                url='{0}/j_security_check'.format(self.base_url),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={'j_username': self.user, 'j_password': self.user_pass},
                timeout=self.timeout
            )
        except ConnectionError:
            raise LoginTimeoutError('Could not connect to {0}'.format(self.vmanage_server))

        if login_result.response.text.startswith('<html>'):
            raise LoginCredentialsError('Could not login to device, check user credentials')
        else:
            return login_result

    def get_banner(self):
        """
        Get vManager banner
        :return: Result named tuple
        """
        url = constants.BANNER_PATH.format(self.base_url)
        return self.get(self.session, url)

    def set_banner(self, banner):
        """
        Set vManage banner
        :param banner: Text of the banner
        :return: Result named tuple
        """
        payload = {'mode': 'on', 'bannerDetail': banner}
        url = constants.BANNER_PATH.format(self.base_url)
        return self.put(self.session, url, data=json.dumps(payload))

    def get_device_by_type(self, device_type='vedges'):
        """
        Get devices from vManage server
        :param device_type: Type of device
        :return: Result named tuple
        """
        if device_type not in ['vedges', 'controllers']:
            raise ValueError('Invalid device type: {0}'.format(device_type))
        url = '{0}/system/device/{1}'.format(self.base_url, device_type)
        return self.get(self.session, url)

    def get_all_devices(self):
        """
        Get a list of all devices
        :return: Result named tuple
        """
        url = '{0}/device'.format(self.base_url)
        return self.get(self.session, url)

    def get_running_config(self, device_uuid, attached=False):
        """
        Get running config of a device
        :param device_uuid: Device's ID
        :param attached: Device attached config
        :return: Result named tuple
        """
        if attached:
            url = '{0}/template/config/attached/{1}'.format(self.base_url, device_uuid)
        else:
            url = '{0}/template/config/running/{1}'.format(self.base_url, device_uuid)
        return self.get(self.session, url)

    def get_device_maps(self):
        """
        Get devices geo location data
        :return: Result named tuple
        """
        url = '{0}/group/map/devices'.format(self.base_url)
        return self.get(self.session, url)

    def get_arp_table(self, device_id):
        """
        Get device arp tables
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/arp?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_bgp_summary(self, device_id):
        """
        Get BGP summary information
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/bgp/summary?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_bgp_routes(self, device_id):
        """
        Get BGP routes
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/bgp/routes?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_bgp_neighbours(self, device_id):
        """
        Get BGP neighbours
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/bgp/neighbors?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_ospf_routes(self, device_id):
        """
        Get OSPF routes
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/ospf/routes?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_ospf_neighbours(self, device_id):
        """
        Get OSPF neighbours
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/ospf/neighbor?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_ospf_database(self, device_id, summary=False):
        """
        Get OSPF database
        :param device_id: device ID
        :param summary: get OSPF database summary
        :return: Result named tuple
        """
        if summary:
            url = '{0}/device/ospf/databasesummary?deviceId={1}'.format(self.base_url, device_id)
        else:
            url = '{0}/device/ospf/database?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_ospf_interfaces(self, device_id):
        """
        Get OSPF interfaces
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/ospf/interface?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_transport_connection(self, device_id):
        """
        Get underlying transport details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/transport/connection?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_tunnel_statistics(self, device_id):
        """
        Get tunnel details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/tunnel/statistics?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_omp_peers(self, device_id, from_vmanage=False):
        """
        Get OMP peers
        :param device_id: device ID
        :param from_vmanage: Get synced peers from vManage server
        :return: Result named tuple
        """
        if from_vmanage:
            url = '{0}/device/omp/synced/peers?deviceId={1}'.format(self.base_url, device_id)
        else:
            url = '{0}/device/omp/peers?deviceId={1}'.format(self.base_url, device_id)

        return self.get(self.session, url)

    def get_omp_summary(self, device_id):
        """
        Get OMP summary
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/omp/summary?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_cellular_modem(self, device_id):
        """
        Get Cellular modem details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/cellular/modem?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_cellular_network(self, device_id):
        """
        Get Cellular network details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/cellular/network?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_cellular_profiles(self, device_id):
        """
        Get Cellular profiles details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/cellular/profiles?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_cellular_radio(self, device_id):
        """
        Get Cellular radio details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/cellular/radio?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_cellular_status(self, device_id):
        """
        Get Cellular status details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/cellular/status?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_cellular_sessions(self, device_id):
        """
        Get Cellular sessions details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/cellular/sessions?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_ipsec_inbound(self, device_id):
        """
        Get IPsec inbound details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/ipsec/inbound?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_ipsec_outbound(self, device_id):
        """
        Get IPsec outbound details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/ipsec/outbound?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_ipsec_localsa(self, device_id):
        """
        Get IPsec local security association details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/ipsec/localsa?deviceId={1}'.format(self.base_url, device_id)
        return self.get(self.session, url)

    def get_template_feature(self, template_id=''):
        """
        Get feature templates
        :param template_id: template ID
        :return: Result named tuple
        """
        url = constants.BASE_TEMPLATE_PATH
        if template_id:
            url += '/object/{1}'.format(self.base_url, template_id)
        return self.get(self.session, url)

    def set_template_aaa(self, data):
        """
        Set AAA template
        """
        url = constants.BASE_TEMPLATE_PATH.format(self.base_url)
        return self.post(self.session, url, data=data)

    def set_template_banner(self, template_name, template_description,
                            device_models=None, login_banner='', motd_banner=''):
        """
        Set device banner template
        :param template_name: Name of template
        :param template_description: Template description
        :param device_models: List of device types
        :param login_banner: Login banner text
        :param motd_banner: MOTD banner text
        :return: Result named tuple
        """
        if not login_banner and not motd_banner:
            raise AttributeError('login_banner and/or motd_banner are required.')

        if isinstance(device_models, str):
            device_models = [device_models]
        elif not isinstance(device_models, list):
            raise AttributeError('Device types should be a list')

        if any(i not in DEVICE_MODEL_MAP for i in device_models):
            raise AttributeError('Invalid device type. Valid types are: {0}'.format(
                ', '.join(DEVICE_MODEL_MAP.keys())
            ))

        template_definition = dict()
        if login_banner:
            template_definition.update({
                'login': vip_object(
                    vip_type=constants.CONSTANT,
                    vip_value=login_banner,
                    vip_variable_name='banner_login')
            })
        if motd_banner:
            template_definition.update({
                'motd': vip_object(
                    vip_type=constants.CONSTANT,
                    vip_value=motd_banner,
                    vip_variable_name='banner_motd')
            })

        payload = utils.create_template_payload(
            name=template_name,
            description=template_description,
            template_type='banner',
            min_version='15.0.0',
            definition=template_definition,
            default=False,
            device_type=device_models,
            device_models=[DEVICE_MODEL_MAP[i] for i in device_models]
        )

        url = constants.BASE_TEMPLATE_PATH.format(self.base_url)
        return self.post(self.session, url, data=json.dumps(payload))

    def set_template_logging(self, template_name, template_description, device_models=None):
        """
        TODO: Add log exporter
        Set device logging template
        :param template_name: Name of template
        :param template_description: Template description
        :param device_models: List of device types
        :return: Result named tuple
        """
        disk_logging = {
            'disk': {
                'enable': vip_object(vip_value='true'),
                'file': {
                    'size': vip_object(vip_value=10),
                    'rotate': vip_object(vip_value=10),
                },
                'priority': vip_object(vip_value='information'),
            }
        }

        template_definition = disk_logging

        payload = utils.create_template_payload(
            name=template_name,
            description=template_description,
            template_type='logging',
            min_version='15.0.0',
            definition=template_definition,
            default=False,
            device_type=device_models,
            device_models=[DEVICE_MODEL_MAP[i] for i in device_models],
        )

        url = constants.BASE_TEMPLATE_PATH.format(self.base_url)
        return self.post(self.session, url, data=json.dumps(payload))

    def set_template_omp(self, template_name, template_description,
                         device_type, device_models=None):
        """
        Set OMP template.
        """
        valid_device_types = [constants.VEDGE, constants.VSMART]
        if device_type not in valid_device_types:
            raise AttributeError('Invalid device type. Valid types are: {0}'.format(
                ', '.join(valid_device_types)
            ))

        vedges = [d for d in constants.ALL_DEVICE_TYPES if constants.VEDGE in d]

        template_definition = dict()

        if device_type == 'vedge':
            template_definition.update({
                'graceful-restart': vip_object(vip_value='true'),
                'send-path-limit': vip_object(vip_value=4),
                'ecmp-limit': vip_object(vip_value=4),
                'shutdown': vip_object(vip_value='false'),
                'timers': {
                    'advertisement-interval': vip_object(vip_value=1),
                    'graceful-restart-timer': vip_object(vip_value=43200),
                    'holdtime': vip_object(vip_value=60),
                    'eor-timer': vip_object(vip_value=300),
                },
                'advertise': {
                    'vipType': 'constant',
                    'vipValue': [
                        {
                            'priority-order': [
                                'protocol',
                                'route'
                            ],
                            'protocol': vip_object(vip_type=constants.CONSTANT, vip_value='ospf'),
                            'route': vip_object(vip_type=constants.CONSTANT, vip_value='external'),
                        },
                        {
                            'priority-order': [
                                'protocol'
                            ],
                            'protocol': vip_object(vip_type=constants.CONSTANT,
                                                   vip_value='connected'),
                        },
                        {
                            'priority-order': [
                                'protocol'
                            ],
                            'protocol': vip_object(vip_type=constants.CONSTANT,
                                                   vip_value='static'),
                        }
                    ],
                    'vipObjectType': 'tree',
                    'vipPrimaryKey': [
                        'protocol'
                    ]
                }
            })

        elif device_type == constants.VSMART:
            template_definition.update({
                'graceful-restart': vip_object(vip_value='true'),
                'send-path-limit': vip_object(vip_value=4),
                'send-backup-paths': vip_object(vip_value='false'),
                'discard-rejected': vip_object(vip_value='false'),
                'shutdown': vip_object(vip_value='false'),
                'timers': {
                    'advertisement-interval': vip_object(vip_value=1),
                    'graceful-restart-timer': vip_object(vip_value=43200),
                    'holdtime': vip_object(vip_value=60),
                    'eor-timer': vip_object(vip_value=300),
                }
            })

        if device_type == constants.VEDGE:
            models = [DEVICE_MODEL_MAP[i] for i in vedges]
        else:
            models = DEVICE_MODEL_MAP[constants.VSMART]

        payload = utils.create_template_payload(
            name=template_name,
            description=template_description,
            template_type='omp-{0}'.format(device_type),
            min_version='15.0.0',
            definition=template_definition,
            device_type=(
                [constants.VSMART] if device_type == constants.VSMART else [i for i in vedges]),
            device_models=models,
            default=False
        )

        url = constants.BASE_TEMPLATE_PATH.format(self.base_url)
        return self.post(self.session, url, data=json.dumps(payload))

    def set_policy_vsmart(self, policy_name, policy_description, policy_configuration):
        """
        vSmart policy
        """
        payload = {
            constants.POLICY_NAME: policy_name,
            constants.POLICY_DESCRIPTION: policy_description,
            constants.POLICY_DEFINITION: policy_configuration,
        }
        url = constants.VSMART_POLICY_PATH.format(self.base_url)
        return self._post(self.session, url, data=json.dumps(payload))

    def set_template_ntp(self, template_name, template_description, ntp_servers=None):
        """
        NTP Template
        """

        def ntp_server_list(ntp_servers):
            """
            Build NTP server list
            """
            for server in ntp_servers:
                yield ({
                    'name': vip_object(vip_type='constant', vip_value=server['ipv4_address']),
                    'key': vip_object(vip_type='ignore'),
                    'vpn': vip_object(vip_type='ignore', vip_value=server['vpn']),
                    'version': vip_object(vip_type='ignore', vip_value=server['version']),
                    'source-interface': vip_object(vip_type='ignore'),
                    'prefer': vip_object(vip_type='constant', vip_value=server['prefer']),
                    'priority-order': [
                        'name',
                        'key',
                        'vpn',
                        'version',
                        'source-interface',
                        'prefer'
                    ]
                })

        payload = {
            'templateName': template_name,
            'templateDescription': template_description,
            'templateType': 'ntp',
            'templateMinVersion': '15.0.0',
            'templateDefinition': {
                'keys': {
                    'trusted': {
                        'vipObjectType': 'list',
                        'vipType': 'ignore'
                    }
                },
                'server': vip_object(
                    vip_type='constant',
                    vip_value=[i for i in ntp_server_list(ntp_servers)],
                    vip_object_type='tree',
                    vip_primary_key=['name']
                ),
            },
            'deviceType': [i for i in DEVICE_MODEL_MAP],
            'deviceModels': [DEVICE_MODEL_MAP[i] for i in DEVICE_MODEL_MAP],
            'factoryDefault': False
        }

        url = constants.BASE_TEMPLATE_PATH.format(self.base_url)
        return self._post(self.session, url, data=json.dumps(payload))

    def set_template_snmpv2(self, template_name, template_description,
                            snmp_contact, v2_community, shutdown='false'):
        """
        SNMP Template
        """
        payload = {
            'templateName': template_name,
            'templateDescription': template_description,
            'templateType': 'snmp',
            'templateMinVersion': '15.0.0',
            'templateDefinition': {
                'shutdown': vip_object(vip_type='constant', vip_value=shutdown),
                'contact': vip_object(vip_type='constant', vip_value=snmp_contact),
                'name': vip_object(vip_type='variable'),
                'location': vip_object(vip_type='variable'),
                'view': {
                    'vipType': 'constant',
                    'vipValue': [
                        {
                            'name': vip_object(vip_type='constant', vip_value=v2_community),
                            'viewMode': 'add',
                            'priority-order': [
                                'name'
                            ]
                        }
                    ],
                    'vipObjectType': 'tree',
                    'vipPrimaryKey': [
                        'name'
                    ]
                },
                'trap': {
                    'group': {
                        'vipType': 'ignore',
                        'vipValue': [
                        ],
                        'vipObjectType': 'tree',
                        'vipPrimaryKey': [
                            'group-name'
                        ]
                    },
                    'target': {
                        'vipType': 'ignore',
                        'vipValue': [
                        ],
                        'vipObjectType': 'tree',
                        'vipPrimaryKey': [
                            'vpn-id',
                            'ip',
                            'port'
                        ]
                    }
                }
            },
            'deviceType': ALL_DEVICE_TYPES,
            'deviceModels': ALL_DEVICE_MODELS,
            'factoryDefault': False
        }

        url = '{0}/template/feature'.format(self.base_url)
        return self._post(self.session, url, data=json.dumps(payload))

    def delete_template(self, template_name='', template_id=''):
        """
        Delete a template
        TODO: Add logic to delete template via name
        """
        if not template_name and not template_id:
            raise AttributeError('Either template_name or template_id is required')
        elif template_name and template_id:
            # add logging to ignore template name
            query = template_id
        else:
            query = find_feature_template(self, template_id)

        url = '{0}/template/feature/{1}'.format(self.base_url, query)
        return self._delete(self.session, url)
