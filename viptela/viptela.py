import os

import copy
import json
import requests

from collections import OrderedDict, namedtuple
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
        reason = HTTP_RESPONSE_CODES[response.status_code]
        error = ''
        if response.json().get('data'):
            json_response = response.json()['data']
        elif response.json().get('config'):
            json_response = response.json()['config']
        elif response.json().get('templateDefinition'):
            json_response = response.json()['templateDefinition']
        else:
            json_response = dict()
            reason = HTTP_RESPONSE_CODES[response.status_code]
            error = 'No data received from device'
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


def create_template_dict(template_dir):
    template_dict = {}
    json_files = [f for f in os.listdir(template_dir) if f.endswith('.json')]
    for file in json_files:
        with open(template_dir + file) as f:
            raw_file = f.read()
        template_dict[file.split('.json')[0]] = json.loads(raw_file)
    return template_dict


def import_provisioning_templates(api_class, template_dict):
    """Import templates from a given template directory into the vManage server."""

    def check_policy(policy_name):
        return_data = api_class.get(
            api_class.session, api_class.base_url + 'template/policy/vedge/'
        )
        for policy in return_data:
            if policy['policyName'] == policy_name:
                return policy['policyId']
        return False

    feature_keys = ["templateName", "templateDescription", "templateType", "templateMinVersion",
                    "deviceType", "factoryDefault", "templateDefinition"]
    policy_keys = ["policyName", "policyDescription", "policyDefinition"]
    device_template_keys = ["templateName", "templateDescription", "deviceType", "configType",
                            "factoryDefault", "policyId", "featureTemplateUidRange",
                            "generalTemplates"]
    device_template_data = template_dict.get('device_template')
    feature_template_id_map = api_class.get(
        api_class.session, api_class.base_url + '/template/device'
    )
    for device_template in device_template_data['templates']:
        template_id_mapping = {}
        feature_data = template_dict.get(
            '{}_features'.format(device_template['templateName']
                                      )
        )
        if not feature_data:
            # TODO: Implement logging here!
            # print "No feature templates"
            continue
        for template_id in feature_data:
            if template_id in feature_data:
                fd = {k: v for k, v in feature_data[template_id].items() if k in feature_keys}
                if fd['templateName'] in feature_template_id_map:
                    new_template_id = feature_template_id_map[fd['templateName']]
                else:
                    post_response = api_class.post(
                        api_class.session, api_class.base_url + '/template/feature',
                        data=json.dumps(fd)
                    )
                    new_template_id = post_response['templateId']
                template_id_mapping[template_id] = new_template_id
        new_device_template = copy.deepcopy(device_template)
        for feature in new_device_template['generalTemplates']:
            feature['templateId'] = template_id_mapping[feature['templateId']]
            if 'subTemplates' in feature:
                for sub_temp in feature['subTemplates']:
                    if 'subTemplates' in sub_temp:
                        for template in sub_temp['subTemplates']:
                            template['templateId'] = template_id_mapping[template['templateId']]
                    sub_temp['templateId'] = template_id_mapping[sub_temp['templateId']]
        if 'featureTemplateUidRange' in new_device_template and new_device_template.get(
                'featureTemplateUidRange'):
            for add_template in new_device_template['featureTemplateUidRange']:
                add_template['templateId'] = template_id_mapping[add_template['templateId']]
        if 'policyId' in device_template and device_template['policyId']:
            policy_data = template_dict.get('{}_policy'.format(device_template['templateName']))
            policy_id = device_template['policyId']
            if policy_id not in policy_data:
                # TODO: Logging here
                # print 'Policy data missing in backup'
                pass
            pd = policy_data[policy_id]
            ch = check_policy(pd['policyName'])
            if ch is False:
                for key in pd.keys():
                    if key not in policy_keys:
                        pd.pop(key, None)
                _ = api_class.post(
                    api_class.session, api_class.base_url + '/template/policy/vedge/',
                    data=json.dumps(pd)
                )
                new_policy_id = check_policy(pd['policyName'])
            else:
                new_policy_id = ch
            new_device_template['policyId'] = new_policy_id
        for key in new_device_template.keys():
            if key not in device_template_keys:
                new_device_template.pop(key, None)
        check_device = False
        for device in api_class.get(api_class.session, api_class.base_url + '/template/device'):
            if device['templateName'] == new_device_template['templateName']:
                check_device = True
                break
        if not check_device:
            _ = api_class.post(
                api_class.session, api_class.base_url + '/template/device/feature/',
                data=json.dumps(new_device_template)
            )
        else:
            # TODO: Logging here
            # print "Skipping %s" % new_device_template["templateName"]
            pass


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
            headers = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}

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
            headers = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}

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
            headers = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}

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
        url = '{0}/settings/configuration/banner'.format(self.base_url)
        return self.get(self.session, url)

    def set_banner(self, banner):
        """
        Set vManage banner
        :param banner: Text of the banner
        :return: Result named tuple
        """
        payload = {'mode': 'on', 'bannerDetail': banner}
        url = '{0}/settings/configuration/banner'.format(self.base_url)
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
        if template_id:
            url = '{0}/template/feature/object/{1}'.format(self.base_url, template_id)
        else:
            url = '{0}/template/feature'.format(self.base_url)
        return self.get(self.session, url)
