"""
Various utilities and helper functions that are implement commonly used features and processes.
"""


import copy
import os
import json
import logging
from collections import namedtuple

from . import constants

# Minor difference between Python2 and Python3
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


logger = logging.getLogger(__name__)

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
        decoded_response = response.json()
        reason = decoded_response[constants.ERROR]['details']
        error = decoded_response[constants.ERROR]['message']
    except JSONDecodeError as e:
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


def vip_object(vip_object_type='object', vip_type=constants.IGNORE, vip_value=None,
               vip_variable_name=None, vip_primary_key=None):
    """
    VIP objects are used as configuration elements
    Build a vip object
    """
    vip = {
        constants.VIP_OBJECT_TYPE: vip_object_type,
        constants.VIP_TYPE: vip_type,
    }

    if vip_value is not None:
        vip.update({constants.VIP_VALUE: vip_value})

    if vip_variable_name is not None:
        vip.update({'vipVariableName': vip_variable_name})

    if vip_primary_key is not None:
        vip.update({constants.VIP_PRIMARY_KEY: vip_primary_key})

    return vip


def create_template_payload(name, description, template_type, min_version, definition, default,
                            device_type, device_models):
    return {
        constants.TEMPLATE_NAME: name,
        constants.TEMPLATE_DESCRIPTION: description,
        constants.TEMPLATE_TYPE: template_type,
        constants.TEMPLATE_MIN_VERSION: min_version,
        constants.TEMPLATE_DEFINITION: definition,
        constants.FACTORY_DEFAULT: default,
        constants.DEVICE_TYPE: list(device_type),
        constants.DEVICE_MODELS: list(device_models),
    }


def check_post_response(response, raise_error=False):
    """Check to see if a post response contains an error code or not. If so, the error is logged,
    and an exception is raised if required."""
    if not response.error:
        return response
    logger.debug('Failure in POST operation: {}.'.format(response.reason))
    if raise_error:
        raise Exception('Failure in POST operation.')
    return response


def import_provisioning_templates(api_class, template_dict):
    """Import templates from into the vManage server."""

    def _check_policy(policy_name):
        return_data = api_class.get(
            api_class.session, api_class.base_url + constants.VEDGE_POLICY_PATH
        ).data
        for policy in return_data:
            if policy[constants.POLICY_NAME] == policy_name:
                return policy[constants.POLICY_ID]
        return False

    device_template_data = template_dict.get('device_template')
    for device_template in device_template_data['templates']:
        id_map = {}
        feature_data = template_dict.get(
            '{}_features'.format(device_template[constants.TEMPLATE_NAME])
        )

        if not feature_data:
            # logger.debug('No feature templates found.')
            continue

        for template_id in feature_data:
            fd = {
                k: v for k, v in feature_data[template_id].items() if k in
                constants.FEATURE_KEYS
            }
            feature_template_id_map_data = api_class.get(
                api_class.session, api_class.base_url + constants.FEATURE_PATH
            ).data
            feature_template_id_map = {
                k[constants.TEMPLATE_NAME]: k[constants.TEMPLATE_ID] for k in
                feature_template_id_map_data
            }

            template_name = fd[constants.TEMPLATE_NAME]
            if template_name in feature_template_id_map:
                new_template_id = feature_template_id_map[template_name]
            else:
                post_response = check_post_response(api_class.post(
                    api_class.session, api_class.base_url + constants.FEATURE_PATH,
                    data=json.dumps(fd)
                ))
                new_template_id = post_response.data[constants.TEMPLATE_ID]
            id_map[template_id] = new_template_id

        new_device_template = copy.deepcopy(device_template)
        for feature in new_device_template[constants.GENERAL_TEMPLATES]:
            feature[constants.TEMPLATE_ID] = id_map[feature[constants.TEMPLATE_ID]]

            for sub_temp in feature.get(constants.SUB_TEMPLATES, []):
                for template in sub_temp.get(constants.SUB_TEMPLATES, []):
                    template[constants.TEMPLATE_ID] = id_map[template[constants.TEMPLATE_ID]]
                sub_temp[constants.TEMPLATE_ID] = id_map[sub_temp[constants.TEMPLATE_ID]]

        for add_template in new_device_template.get(constants.UID_RANGE, []):
            add_template[constants.TEMPLATE_ID] = id_map[add_template[constants.TEMPLATE_ID]]

        if device_template.get(constants.POLICY_ID):
            policy_data = template_dict.get(
                '{}_policy'.format(device_template[constants.TEMPLATE_NAME]), {}
            )
            policy_id = device_template[constants.POLICY_ID]

            if policy_id not in policy_data:
                # logger.debug('Policy data missing in source templates.')
                pass
            pd = policy_data[policy_id]
            new_policy_id = _check_policy(pd[constants.POLICY_NAME])

            if not new_policy_id:
                pd = {k: v for k, v in pd.items() if k in constants.POLICY_KEYS}
                _ = check_post_response(api_class.post(
                    api_class.session, api_class.base_url + constants.VEDGE_POLICY_PATH,
                    data=json.dumps(pd))
                )
                new_policy_id = _check_policy(pd[constants.POLICY_NAME])
            new_device_template[constants.POLICY_ID] = new_policy_id

        new_device_template = {
            k: v for k, v in new_device_template.items() if k in constants.DEVICE_TEMPLATE_KEYS
        }
        template_exists = False
        for device in api_class.get(
                api_class.session, api_class.base_url + constants.DEVICE_PATH
        ).data:
            if device[constants.TEMPLATE_NAME] == new_device_template[constants.TEMPLATE_NAME]:
                template_exists = True
                break

        if not template_exists:
            _ = check_post_response(api_class.post(
                api_class.session, api_class.base_url + constants.DEVICE_FEATURE_PATH,
                data=json.dumps(new_device_template)
            ))
        else:
            # TODO: Logging here
            # logger.debug('Skipping {} - template already exists'.format(
            #     new_device_template[constants.TEMPLATE_NAME]
            # ))
            pass
    return
