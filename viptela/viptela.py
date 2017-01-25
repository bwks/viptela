import requests

from collections import namedtuple
from . exceptions import LoginCredentialsError

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
    HTTP 2XX
    :param response: requests response object
    :return: namedtuple result object
    """
    if response.request.method in ['GET']:
        try:
            json_response = response.json()['data'] if response.json()['data'] else dict()
            reason = HTTP_RESPONSE_CODES[response.status_code]
            error = ''
        except KeyError as e:
            json_response = dict()
            reason = 'No data received from device'
            error = e
        except ValueError as e:
            json_response = dict()
            reason = 'No data received from device'
            error = e
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
    HTTP 4XX and 5XX
    :param response: requests response object
    :return: namedtuple result object
    """
    json_response = dict()
    reason = response.json()['error']['details']
    error = response.json()['error']['message']

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
    def _get(session, url, headers=None):
        """
        Perform a HTTP get
        :param session: requests session
        :param url: url to get
        :param headers: HTTP headers
        :return:
        """
        if headers is None:
            headers = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}

        return parse_response(session.get(url=url, headers=headers))

    @staticmethod
    def _put(session, url, headers=None, data=None):
        """
        Perform a HTTP put
        :param session: requests session
        :param url: url to get
        :param headers: HTTP headers
        :param data: Data payload
        :return:
        """
        if headers is None:
            # add default headers for put
            headers = dict()

        if data is None:
            data = dict()
        pass

    @staticmethod
    def _post(session, url, headers=None, data=None):
        """
        Perform a HTTP post
        :param session: requests session
        :param url: url to post
        :param headers: HTTP headers
        :param data: Data payload
        :return:
        """
        if headers is None:
            # add default headers for post
            headers = dict()

        if data is None:
            data = dict()

        return parse_response(session.post(url=url, headers=headers, data=data))

    @staticmethod
    def _delete(session, url, headers=None, data=None):
        """
        Perform a HTTP delete
        :param session: requests session
        :param url: url to delete
        :param headers: HTTP headers
        :param data: Data payload
        :return:
        """
        if headers is None:
            # add default headers for delete
            headers = dict()

        if data is None:
            data = dict()

        pass

    def __init__(self, user, user_pass, vmanage_server, vmanage_server_port=8443, verify=False):
        """
        Init method for Viptela class
        :param user: API user name
        :param user_pass: API user password
        :param vmanage_server: vManage server IP address or Hostname
        :param vmanage_server_port: vManage API port
        :param verify: Verify HTTPs certificate
        """
        self.user = user
        self.user_pass = user_pass
        self.vmanage_server = vmanage_server
        self.vmanage_server_port = vmanage_server_port
        self.verify = verify

        self.base_url = 'https://{0}:{1}/dataservice'.format(
            self.vmanage_server,
            self.vmanage_server_port
        )

        self.session = requests.session()
        if not self.verify:
            self.session.verify = self.verify

        # login
        login_result = self._post(
            session=self.session,
            url='{0}/j_security_check'.format(self.base_url),
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={'j_username': self.user, 'j_password': self.user_pass}
        )

        if login_result.response.text.startswith('<html>'):
            raise LoginCredentialsError('Could not login to device, check user credentials')
        else:
            self.login_result = login_result

    def get_device_by_type(self, device_type='vedges'):
        """
        Get devices from vManage server
        :param device_type: Type of device
        :return:
        """
        if device_type not in ['vedges', 'controllers']:
            raise ValueError('Invalid device type: {0}'.format(device_type))
        url = '{0}/system/device/{1}'.format(self.base_url, device_type)
        return self._get(self.session, url)

    def get_all_devices(self):
        """
        Get a list of all devices
        :return:
        """
        url = '{0}/device'.format(self.base_url)
        return self._get(self.session, url)

# Not working
#    def get_running_config(self, device_id, xml=False):
#        """
#        Get running config of a device
#        :param device_id: Device's ID
#        :param xml: Return config in XML format
#        :return:
#        """
#        # url = '{0}/template/config/running/{1}'.format(self.base_url, device_id)
#        # url = '{0}/config?deviceId={1}'.format(self.base_url, device_id)
#        return self._get(self.session, url)

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
        if not summary:
            url = '{0}/device/ospf/database?deviceId={1}'.format(self.base_url, device_id)
        else:
            url = '{0}/device/ospf/databasesummary?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)

    def get_ospf_interfaces(self, device_id):
        """
        Get OSPF interfaces
        :param device_id: device ID
        :return: Result named tuple
        """
        url = '{0}/device/ospf/interface?deviceId={1}'.format(self.base_url, device_id)
        return self._get(self.session, url)
