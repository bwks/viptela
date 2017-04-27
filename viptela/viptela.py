import json
import requests

from collections import namedtuple
from requests.exceptions import ConnectionError
from . exceptions import LoginCredentialsError, LoginTimeoutError

HTTP_SUCCESS_CODES = {
    200: 'Success',
}

HTTP_ERROR_CODES = {
    400: 'Bad Request',
    403: 'Forbidden',
    404: 'API Not found',
    406: 'Not Acceptable Response',
    415: 'Unsupported Media Type',
    500: 'Internal Server Error'
}

HTTP_RESPONSE_CODES = dict()
HTTP_RESPONSE_CODES.update(HTTP_SUCCESS_CODES)
HTTP_RESPONSE_CODES.update(HTTP_ERROR_CODES)

DEVICE_MODEL_MAP = {
    'vedge-cloud': {'name': 'vedge-cloud','displayName':'vEdge Cloud','deviceType': 'vedge'},
    'vedge-100': {'name': 'vedge-100', 'displayName': 'vEdge 100', 'deviceType': 'vedge'},
    'vedge-100-B': {'name':'vedge-100-B','displayName':'vEdge 100 B','deviceType':'vedge'},
    'vedge-100-M': {'name':'vedge-100-M','displayName':'vEdge 100 M','deviceType':'vedge'},
    'vedge-100-WM': {'name':'vedge-100-WM','displayName':'vEdge 100 WM','deviceType':'vedge'},
    'vedge-1000': {'name':'vedge-1000','displayName':'vEdge 1000','deviceType':'vedge'},            
    'vedge-2000': {'name':'vedge-2000','displayName':'vEdge 2000','deviceType':'vedge'},
    'vmanage': {'name':'vmanage','displayName':'vManage','deviceType':'vmanage'},
    'vsmart': {'name':'vsmart','displayName':'vSmart','deviceType':'vsmart'},            
}

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

    if not response.content and response.request.method in ['GET', 'POST']:
        json_response = dict()
        reason = HTTP_RESPONSE_CODES[response.status_code]
        error = ''

    elif response.request.method in ['GET', 'POST']:
        reason = HTTP_RESPONSE_CODES[response.status_code]
        error = ''
        json_response = response.json()
        # if response.json().get('data'):
        #     json_response = response.json()['data']
        # elif response.json().get('config'):
        #     json_response = response.json()['config']
        # elif response.json().get('templateDefinition'):
        #     json_response = response.json()['templateDefinition']
        # elif response.json().get('templateId'):
        #     json_response = response.json()['templateId']
        # else:
        #     json_response = dict()
        #     reason = HTTP_RESPONSE_CODES[response.status_code]
        #     error = 'No data received from device'
    else:
        json_response = dict()
        reason = HTTP_RESPONSE_CODES[response.status_code]
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
        reason = response.json()['error']['details']
        error = response.json()['error']['message']
    except ValueError as e:
        json_response = dict()
        reason = HTTP_RESPONSE_CODES[response.status_code]
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
    if response.status_code in HTTP_SUCCESS_CODES:
        return parse_http_success(response)

    elif response.status_code in HTTP_ERROR_CODES:
        return parse_http_error(response)


class Viptela(object):
    """
    Class for use with Viptela vManage API.
    """
    @staticmethod
    def _get(session, url, headers=None, timeout=10):
        """
        Perform a HTTP get
        :param session: requests session
        :param url: url to get
        :param headers: HTTP headers
        :param timeout: Timeout for request response
        :return:
        """
        if headers is None:
            headers = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}

        return parse_response(session.get(url=url, headers=headers, timeout=timeout))

    @staticmethod
    def _put(session, url, headers=None, data=None, timeout=10):
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
            headers = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}

        if data is None:
            data = dict()

        return parse_response(session.put(url=url, headers=headers, data=data, timeout=timeout))

    @staticmethod
    def _post(session, url, headers=None, data=None, timeout=10):
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
            headers = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}

        if data is None:
            data = dict()

        return parse_response(session.post(url=url, headers=headers, data=data, timeout=timeout))

    @staticmethod
    def _delete(session, url, headers=None, data=None, timeout=10):
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
            headers = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}

        if data is None:
            data = dict()

        pass

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
            login_result = self._post(
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
        url = '{0}/settings/configuration/banner'.format(self.base_url)
        return self._get(self.session, url)

    def set_banner(self, banner):
        """
        Set vManage banner
        :param banner: Text of the banner
        :return: Result named tuple
        """
        payload = {'mode': 'on', 'bannerDetail': banner}
        url = '{0}/settings/configuration/banner'.format(self.base_url)
        return self._put(self.session, url, data=json.dumps(payload))

    def get_device_by_type(self, device_type='vedges'):
        """
        Get devices from vManage server
        :param device_type: Type of device
        :return: Result named tuple
        """
        if device_type not in ['vedges', 'controllers']:
            raise ValueError('Invalid device type: {0}'.format(device_type))
        url = '{0}/system/device/{1}'.format(self.base_url, device_type)
        return self._get(self.session, url)

    def get_all_devices(self):
        """
        Get a list of all devices
        :return: Result named tuple
        """
        url = '{0}/device'.format(self.base_url)
        return self._get(self.session, url)

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
        return self._get(self.session, url)

    def get_device_maps(self):
        """
        Get devices geo location data
        :return: Result named tuple
        """
        url = '{0}/group/map/devices'.format(self.base_url)
        return self._get(self.session, url)

    def get_arp_table(self, device_id):
        """
        Get device arp tables
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/arp?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_bgp_summary(self, device_id):
        """
        Get BGP summary information
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/bgp/summary?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_bgp_routes(self, device_id):
        """
        Get BGP routes
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/bgp/routes?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_bgp_neighbours(self, device_id):
        """
        Get BGP neighbours
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/bgp/neighbors?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_ospf_routes(self, device_id):
        """
        Get OSPF routes
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/ospf/routes?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_ospf_neighbours(self, device_id):
        """
        Get OSPF neighbours
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/ospf/neighbor?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

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
        return self._get(self.session, url)

    def get_ospf_interfaces(self, device_id):
        """
        Get OSPF interfaces
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/ospf/interface?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_transport_connection(self, device_id):
        """
        Get underlying transport details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/transport/connection?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_tunnel_statistics(self, device_id):
        """
        Get tunnel details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/tunnel/statistics?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

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

        return self._get(self.session, url)

    def get_omp_summary(self, device_id):
        """
        Get OMP summary
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/omp/summary?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_cellular_modem(self, device_id):
        """
        Get Cellular modem details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/cellular/modem?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_cellular_network(self, device_id):
        """
        Get Cellular network details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/cellular/network?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_cellular_profiles(self, device_id):
        """
        Get Cellular profiles details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/cellular/profiles?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_cellular_radio(self, device_id):
        """
        Get Cellular radio details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/cellular/radio?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_cellular_status(self, device_id):
        """
        Get Cellular status details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/cellular/status?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_cellular_sessions(self, device_id):
        """
        Get Cellular sessions details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/cellular/sessions?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_ipsec_inbound(self, device_id):
        """
        Get IPsec inbound details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/ipsec/inbound?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_ipsec_outbound(self, device_id):
        """
        Get IPsec outbound details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/ipsec/outbound?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_ipsec_localsa(self, device_id):
        """
        Get IPsec local security association details
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/ipsec/localsa?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_template_feature(self, template_id=''):
        """
        Get feature templates
        :param template_id: template ID
        :return: Result named tuple
        """
        if template_id:
            url = '{0}/template/feature/object/{1}'.format(self.base_url, template_id)
        else:
            url = '{0}/template/feature'.format(self.base_url)
        return self._get(self.session, url)

    def set_template_aaa(self, data):
        url = '{0}/template/feature'.format(self.base_url)
        return self._post(self.session, url, data=data)

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
                'login': {
                    'vipObjectType': 'object', 
                    'vipType': 'constant', 
                    'vipValue': login_banner, 
                    'vipVariableName': 'banner_login'
                    }
                })
        if motd_banner:
            template_definition.update({
                'motd': {
                    'vipObjectType': 'object', 
                    'vipType': 'constant', 
                    'vipValue': motd_banner, 
                    'vipVariableName': 'banner_motd'
                    }
                })

        payload = {
            'templateName': template_name,
            'templateDescription': template_description,
            'templateType': 'banner',
            'templateMinVersion': '15.0.0',
            'templateDefinition': template_definition,
            'factoryDefault': False,
            'deviceType': device_models, 
            'deviceModels': [DEVICE_MODEL_MAP[i] for i in device_models],
        }

        url = '{0}/template/feature'.format(self.base_url)
        return self._post(self.session, url, data=json.dumps(payload))

    def set_template_logging(self, template_name, template_description, 
                             device_types, device_models=None, ):
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
                'enable': {  
                    'vipObjectType': 'object',
                    'vipType': 'ignore',
                    'vipValue': 'true'
                },
                'file': {  
                    'size': {  
                        'vipObjectType': 'object',
                        'vipType': 'ignore',
                        'vipValue': 10
                    },
                    'rotate': {  
                        'vipObjectType': 'object',
                        'vipType': 'ignore',
                        'vipValue': 10
                    }
                },
                'priority': {  
                    'vipObjectType': 'object',
                    'vipType': 'ignore',
                    'vipValue': 'information'
                }
            }
        }

        template_definition = disk_logging

        payload = {
            'templateName': template_name,
            'templateDescription': template_description,
            'templateType':'logging',
            'templateMinVersion':'15.0.0',
            'templateDefinition': template_definition,
            'factoryDefault': False,
            'deviceType': device_models, 
            'deviceModels': [DEVICE_MODEL_MAP[i] for i in device_models],
        }

        url = '{0}/template/feature'.format(self.base_url)
        return self._post(self.session, url, data=json.dumps(payload))

    def set_template_omp(self, template_name, template_description, 
                         device_type, device_models=None):

        valid_device_types = ['vedge', 'vsmart']
        if device_type not in valid_device_types:
            raise AttributeError('Invalid device type. Valid types are: {0}'.format(
                ', '.join(valid_device_types)
            ))

        vedges = [
            'vedge-cloud', 'vedge-100', 'vedge-100-B', 'vedge-100-M', 
            'vedge-100-WM', 'vedge-1000', 'vedge-2000',
        ]

        template_definition = dict()

        if device_type == 'vedge':
            template_definition.update({
                    'graceful-restart': {  
                        'vipObjectType': 'object',
                        'vipType': 'ignore',
                        'vipValue': 'true'
                    },
                    'send-path-limit': {  
                        'vipObjectType': 'object',
                        'vipType': 'ignore',
                        'vipValue': 4
                    },
                    'ecmp-limit': {  
                        'vipObjectType': 'object',
                        'vipType': 'ignore',
                        'vipValue': 4
                    },
                    'shutdown': {  
                        'vipObjectType': 'object',
                        'vipType': 'ignore',
                        'vipValue': 'false'
                    },
                    'timers': {  
                        'advertisement-interval': {  
                            'vipObjectType': 'object',
                            'vipType': 'ignore',
                            'vipValue': 1
                        },
                        'graceful-restart-timer': {  
                            'vipObjectType': 'object',
                            'vipType': 'ignore',
                            'vipValue': 43200
                        },
                        'holdtime': {  
                            'vipObjectType': 'object',
                            'vipType': 'ignore',
                            'vipValue': 60
                        },
                        'eor-timer': {  
                            'vipObjectType': 'object',
                            'vipType': 'ignore',
                            'vipValue': 300
                        }
                    },
                    'advertise': {  
                        'vipType':'constant',
                        'vipValue': [  
                            {  
                                'priority-order': [  
                                    'protocol',
                                    'route'
                                ],
                                'protocol': {  
                                    'vipType': 'constant',
                                    'vipValue': 'ospf',
                                    'vipObjectType': 'object'
                                },
                                'route': {  
                                    'vipType': 'constant',
                                    'vipValue': 'external',
                                    'vipObjectType': 'object'
                                }
                            },
                            {  
                                'priority-order': [  
                                    'protocol'
                                ],
                                'protocol': {  
                                    'vipType': 'constant',
                                    'vipValue': 'connected',
                                    'vipObjectType': 'object'
                                }
                            },
                            {  
                                'priority-order':  [  
                                    'protocol'
                                ],
                                'protocol': {  
                                    'vipType': 'constant',
                                    'vipValue': 'static',
                                    'vipObjectType': 'object'
                                }
                            }
                        ],
                        'vipObjectType': 'tree',
                        'vipPrimaryKey': [  
                            'protocol'
                        ]
                    }
                })

        elif device_type == 'vsmart':
            template_definition.update({
                    'graceful-restart': {  
                        'vipObjectType': 'object',
                        'vipType': 'ignore',
                        'vipValue': 'true'
                    },
                    'send-path-limit': {  
                        'vipObjectType': 'object',
                        'vipType': 'ignore',
                        'vipValue': 4
                    },
                    'send-backup-paths': {  
                        'vipObjectType': 'object',
                        'vipType': 'ignore',
                        'vipValue': 'false'
                    },
                    'discard-rejected': {  
                        'vipObjectType': 'object',
                        'vipType': 'ignore',
                        'vipValue': 'false'
                    },
                    'shutdown': {  
                        'vipObjectType': 'object',
                        'vipType': 'ignore',
                        'vipValue': 'false'
                    },
                    'timers': {  
                        'advertisement-interval': {  
                            'vipObjectType': 'object',
                            'vipType': 'ignore',
                            'vipValue': 1
                        },
                        'graceful-restart-timer': {  
                            'vipObjectType': 'object',
                            'vipType': 'ignore',
                            'vipValue': 43200
                        },
                        'holdtime': {  
                            'vipObjectType': 'object',
                            'vipType': 'ignore',
                            'vipValue': 60
                        },
                        'eor-timer': {  
                            'vipObjectType': 'object',
                            'vipType': 'ignore',
                            'vipValue': 300
                        }
                    }
                })

        if device_type == 'vedge':
            models = [DEVICE_MODEL_MAP[i] for i in vedges]
        else:
            models = DEVICE_MODEL_MAP['vsmart']

        payload = {  
            'templateName': template_name,
            'templateDescription': template_description,
            'templateType': 'omp-{0}'.format(device_type),
            'templateMinVersion': '15.0.0',
            'templateDefinition': template_definition,
            'deviceType': [i if device_type == 'vedge' else 'vsmart' for i in vedges],
            'deviceModels': models,
            'factoryDefault': False
        }

        url = '{0}/template/feature'.format(self.base_url)
        return self._post(self.session, url, data=json.dumps(payload))

    def set_policy_vsmart(self, policy_name, policy_description, policy_configuration):
        payload = {  
            'policyName': policy_name,
            'policyDescription':  policy_description,
            'policyDefinition': policy_configuration,
        }
        url = '{0}/template/policy/vsmart'.format(self.base_url)
        return self._post(self.session, url, data=json.dumps(payload))