"""Base API class and functions used by the API."""


import json
import requests

from requests.exceptions import ConnectionError

from . import constants, exceptions, utils


class Viptela(object):
    """
    Class for use with Viptela vManage API.
    """

    @staticmethod
    def get(session, url, headers=None, timeout=constants.STANDARD_HTTP_TIMEOUT):
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

        return utils.parse_response(session.get(url=url, headers=headers, timeout=timeout))

    @staticmethod
    def put(session, url, headers=None, data=None, timeout=constants.STANDARD_HTTP_TIMEOUT):
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

        return utils.parse_response(
            session.put(url=url, headers=headers, data=data, timeout=timeout)
        )

    @staticmethod
    def post(session, url, headers=None, data=None, timeout=constants.STANDARD_HTTP_TIMEOUT):
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

        return utils.parse_response(
            session.post(url=url, headers=headers, data=data, timeout=timeout)
        )

    @staticmethod
    def delete(session, url, headers=None, data=None, timeout=constants.STANDARD_HTTP_TIMEOUT):
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

        return utils.parse_response(
            session.delete(url=url, headers=headers, data=data, timeout=timeout)
        )

    def __init__(self, user, user_pass, vmanage_server, vmanage_server_port=8443,
                 verify=False, disable_warnings=False, timeout=constants.STANDARD_HTTP_TIMEOUT,
                 auto_login=True):
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
        # Mapping between US and British style spelling.
        self.get_bgp_neighbors = self.get_bgp_neighbours
        self.get_ospf_neighbors = self.get_ospf_neighbours

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
            raise exceptions.LoginTimeoutError(
                'Could not connect to {0}'.format(self.vmanage_server)
            )

        if login_result.response.text.startswith('<html>'):
            raise exceptions.LoginCredentialsError(
                'Could not login to device, check user credentials'
            )
        else:
            return login_result

    def get_banner(self):
        """
        Get vManager banner
        :return: Result named tuple
        """
        url = constants.BANNER_PATH_W_BASE.format(self.base_url)
        return self.get(self.session, url)

    def set_banner(self, banner):
        """
        Set vManage banner
        :param banner: Text of the banner
        :return: Result named tuple
        """
        payload = {'mode': 'on', 'bannerDetail': banner}
        url = constants.BANNER_PATH_W_BASE.format(self.base_url)
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
        url = '{}/device'.format(self.base_url)
        return self.get(self.session, url)

    def get_running_config(self, device_uuid, attached=False):
        """
        Get running config of a device
        :param device_uuid: Device's ID
        :param attached: Device attached config
        :return: Result named tuple
        """
        url = '{}/template/config/'.format(self.base_url)
        if attached:
            url += 'attached/{}'.format(device_uuid)
        else:
            url += 'running/{}'.format(device_uuid)
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
        url = '{}/device/omp/'.format(self.base_url)
        if from_vmanage:
            url += 'synced/peers?deviceId={}'.format(device_id)
        else:
            url += 'peers?deviceId={}'.format(device_id)

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
        url = constants.BASE_TEMPLATE_PATH_W_BASE.format(self.base_url)
        if template_id:
            url += '/object/{0}'.format(template_id)
        return self.get(self.session, url)

    def set_template_aaa(self, data):
        """
        Set AAA template
        """
        url = constants.BASE_TEMPLATE_PATH_W_BASE.format(self.base_url)
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

        if any(i not in constants.DEVICE_MODEL_MAP for i in device_models):
            raise AttributeError('Invalid device type. Valid types are: {0}'.format(
                ', '.join(constants.ALL_DEVICE_TYPES)
            ))

        template_definition = dict()
        if login_banner:
            template_definition.update({
                'login': utils.vip_object(
                    vip_type=constants.CONSTANT,
                    vip_value=login_banner,
                    vip_variable_name='banner_login')
            })
        if motd_banner:
            template_definition.update({
                'motd': utils.vip_object(
                    vip_type=constants.CONSTANT,
                    vip_value=motd_banner,
                    vip_variable_name='banner_motd')
            })

        payload = utils.create_template_payload(
            name=template_name,
            description=template_description,
            template_type='banner',
            min_version=constants.V_15,
            definition=template_definition,
            default=False,
            device_type=device_models,
            device_models=constants.ALL_DEVICE_MODELS
        )

        url = constants.BASE_TEMPLATE_PATH_W_BASE.format(self.base_url)
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
                'enable': utils.vip_object(vip_value=constants.TRUE),
                'file': {
                    'size': utils.vip_object(vip_value=10),
                    'rotate': utils.vip_object(vip_value=10),
                },
                'priority': utils.vip_object(vip_value='information'),
            }
        }

        template_definition = disk_logging

        payload = utils.create_template_payload(
            name=template_name,
            description=template_description,
            template_type='logging',
            min_version=constants.V_15,
            definition=template_definition,
            default=False,
            device_type=device_models,
            device_models=constants.ALL_DEVICE_MODELS,
        )

        url = constants.BASE_TEMPLATE_PATH_W_BASE.format(self.base_url)
        return self.post(self.session, url, data=json.dumps(payload))

    def set_template_omp(self, template_name, template_description, device_type):
        """
        Set OMP template.
        """
        valid_device_types = [constants.VEDGE, constants.VSMART]
        if device_type not in valid_device_types:
            raise AttributeError('Invalid device type. Valid types are: {0}'.format(
                ', '.join(valid_device_types)
            ))

        vedges = [d for d in constants.ALL_DEVICE_TYPES if constants.VEDGE in d]

        template_definition = {
                'graceful-restart': utils.vip_object(vip_value=constants.TRUE),
                'send-path-limit': utils.vip_object(vip_value=4),
                'shutdown': utils.vip_object(vip_value=constants.FALSE),
                'timers': {
                    'advertisement-interval': utils.vip_object(vip_value=1),
                    'graceful-restart-timer': utils.vip_object(vip_value=43200),
                    'holdtime': utils.vip_object(vip_value=60),
                    'eor-timer': utils.vip_object(vip_value=300),
                }
            }

        if device_type == constants.VEDGE:
            template_definition.update({
                'ecmp-limit': utils.vip_object(vip_value=4),
                'timers': {
                    'advertisement-interval': utils.vip_object(vip_value=1),
                    'graceful-restart-timer': utils.vip_object(vip_value=43200),
                    'holdtime': utils.vip_object(vip_value=60),
                    'eor-timer': utils.vip_object(vip_value=300),
                },
                'advertise': {
                    constants.VIP_TYPE: constants.CONSTANT,
                    constants.VIP_VALUE: [
                        {
                            constants.PRIORITY_ORDER: [
                                constants.PROTOCOL,
                                'route'
                            ],
                            constants.PROTOCOL: utils.vip_object(vip_type=constants.CONSTANT,
                                                                 vip_value='ospf'),
                            'route': utils.vip_object(vip_type=constants.CONSTANT,
                                                      vip_value='external'),
                        },
                        {
                            constants.PRIORITY_ORDER: [
                                constants.PROTOCOL
                            ],
                            constants.PROTOCOL: utils.vip_object(vip_type=constants.CONSTANT,
                                                                 vip_value='connected'),
                        },
                        {
                            constants.PRIORITY_ORDER: [
                                constants.PROTOCOL
                            ],
                            constants.PROTOCOL: utils.vip_object(vip_type=constants.CONSTANT,
                                                                 vip_value='static'),
                        }
                    ],
                    constants.VIP_OBJECT_TYPE: constants.TREE,
                    constants.VIP_PRIMARY_KEY: [
                        constants.PROTOCOL
                    ]
                }
            })
            models = [constants.DEVICE_MODEL_MAP[i] for i in vedges]

        else:
            template_definition.update({
                'send-backup-paths': utils.vip_object(vip_value=constants.FALSE),
                'discard-rejected': utils.vip_object(vip_value=constants.FALSE),
            })
            models = constants.DEVICE_MODEL_MAP[constants.VSMART]

        payload = utils.create_template_payload(
            name=template_name,
            description=template_description,
            template_type='omp-{0}'.format(device_type),
            min_version=constants.V_15,
            definition=template_definition,
            device_type=(
                [constants.VSMART] if device_type == constants.VSMART else [i for i in vedges]),
            device_models=models,
            default=False
        )

        url = constants.BASE_TEMPLATE_PATH_W_BASE.format(self.base_url)
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
        url = constants.VSMART_POLICY_PATH_W_BASE.format(self.base_url)
        return self.post(self.session, url, data=json.dumps(payload))

    def set_template_ntp(self, template_name, template_description, ntp_servers=None):
        """
        NTP Template
        """

        def ntp_server_list(server_list):
            """
            Build NTP server list
            """
            for server in server_list:
                yield ({
                    constants.NAME: utils.vip_object(vip_type=constants.CONSTANT,
                                                     vip_value=server['ipv4_address']),
                    'key': utils.vip_object(vip_type=constants.IGNORE),
                    'vpn': utils.vip_object(vip_type=constants.IGNORE, vip_value=server['vpn']),
                    'version': utils.vip_object(
                        vip_type=constants.IGNORE, vip_value=server['version']),
                    'source-interface': utils.vip_object(vip_type=constants.IGNORE),
                    'prefer': utils.vip_object(
                        vip_type=constants.CONSTANT, vip_value=server['prefer']),
                    'priority-order': [
                        constants.NAME,
                        'key',
                        'vpn',
                        'version',
                        'source-interface',
                        'prefer'
                    ]
                })

        payload = utils.create_template_payload(
            name=template_name,
            description=template_description,
            template_type='ntp',
            min_version=constants.V_15,
            definition={
                'keys': {
                    'trusted': {
                        constants.VIP_OBJECT_TYPE: 'list',
                        constants.VIP_TYPE: 'ignore'
                    }
                },
                'server': utils.vip_object(
                    vip_type=constants.CONSTANT,
                    vip_value=[i for i in ntp_server_list(ntp_servers)],
                    vip_object_type=constants.TREE,
                    vip_primary_key=[constants.NAME]
                ),
            },
            device_type=constants.ALL_DEVICE_TYPES,
            device_models=constants.ALL_DEVICE_MODELS,
            default=False
        )

        url = constants.BASE_TEMPLATE_PATH_W_BASE.format(self.base_url)
        return self.post(self.session, url, data=json.dumps(payload))

    def set_template_snmpv2(self, template_name, template_description,
                            snmp_contact, v2_community, shutdown=constants.FALSE):
        """
        SNMP Template
        """
        payload = utils.create_template_payload(
            name=template_name,
            description=template_description,
            template_type='snmp',
            min_version=constants.V_15,
            definition={
                'shutdown': utils.vip_object(vip_type=constants.CONSTANT, vip_value=shutdown),
                'contact': utils.vip_object(vip_type=constants.CONSTANT, vip_value=snmp_contact),
                constants.NAME: utils.vip_object(vip_type=constants.VARIABLE),
                'location': utils.vip_object(vip_type=constants.VARIABLE),
                'view': {
                    constants.VIP_TYPE: constants.CONSTANT,
                    constants.VIP_VALUE: [
                        {
                            constants.NAME: utils.vip_object(
                                vip_type=constants.CONSTANT, vip_value=v2_community),
                            'viewMode': 'add',
                            'priority-order': [
                                constants.NAME
                            ]
                        }
                    ],
                    constants.VIP_OBJECT_TYPE: constants.TREE,
                    constants.VIP_PRIMARY_KEY: [
                        constants.NAME
                    ]
                },
                'trap': {
                    'group': {
                        constants.VIP_TYPE: constants.IGNORE,
                        constants.VIP_VALUE: [
                        ],
                        constants.VIP_OBJECT_TYPE: constants.TREE,
                        constants.VIP_PRIMARY_KEY: [
                            'group-name'
                        ]
                    },
                    'target': {
                        constants.VIP_TYPE: constants.IGNORE,
                        constants.VIP_VALUE: [
                        ],
                        constants.VIP_OBJECT_TYPE: constants.TREE,
                        constants.VIP_PRIMARY_KEY: [
                            'vpn-id',
                            'ip',
                            'port'
                        ]
                    }
                }
            },
            device_type=constants.ALL_DEVICE_TYPES,
            device_models=constants.ALL_DEVICE_MODELS,
            default=False
        )

        url = constants.BASE_TEMPLATE_PATH_W_BASE.format(self.base_url)
        return self.post(self.session, url, data=json.dumps(payload))

    def delete_template(self, template_name='', template_id=''):
        """
        Delete a template
        TODO: Add logic to delete template via name
        """
        if not template_name and not template_id:
            raise AttributeError('Either template_name or template_id is required')
        elif template_id:
            # add logging to ignore template name
            query = template_id
        else:
            query = utils.find_feature_template(self, template_name)

        url = constants.BASE_TEMPLATE_PATH_W_BASE.format(self.base_url) + '/{}'.format(query)
        return self.delete(self.session, url)
