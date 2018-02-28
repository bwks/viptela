"""
Various utilities and helper functions that are implement commonly used features and processes.
"""


import copy
import os
import json
import logging

from . import constants


logger = logging.getLogger(__name__)


def create_template_payload(name, description, template_type, min_version, definition, default,
                            device_type, device_models):
    return {
        constants.TEMPLATE_NAME: name,
        constants.TEMPLATE_DESCRIPTION: description,
        constants.TEMPLATE_TYPE: template_type,
        constants.TEMPLATE_MIN_VERSION: min_version,
        constants.TEMPLATE_DEFINITION: definition,
        constants.FACTORY_DEFAULT: default,
        constants.DEVICE_TYPE: device_type,
        constants.DEVICE_MODELS: device_models,
    }


def create_template_dict(template_dir):
    """Create a dict containing all of the JSON from a template directory for the vManage server."""
    if not template_dir.endswith('/'):
        template_dir += '/'
    template_dict = {}
    json_files = [f for f in os.listdir(template_dir) if f.endswith('.json')]
    for file in json_files:
        with open(template_dir + file) as f:
            template_dict[file.split('.json')[0]] = json.loads(f.read())
    return template_dict


def import_provisioning_templates(api_class, template_dict):
    """Import templates from into the vManage server."""

    def check_policy(policy_name):
        return_data = api_class.get(
            api_class.session, api_class.base_url + constants.VEDGE_POLICY_PATH
        ).data
        for policy in return_data:
            if policy[constants.POLICY_NAME] == policy_name:
                return policy[constants.POLICY_ID]
        return False
    device_template_data = template_dict.get('device_template')
    for device_template in device_template_data['templates']:
        template_id_mapping = {}
        feature_data = template_dict.get(
            '{}_features'.format(device_template[constants.TEMPLATE_NAME])
        )
        if not feature_data:
            # logger.debug('No feature templates found.')
            continue
        for template_id in feature_data:
            if template_id in feature_data:
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
                if fd[constants.TEMPLATE_NAME] in feature_template_id_map:
                    new_template_id = feature_template_id_map[fd[constants.TEMPLATE_NAME]]
                else:
                    post_response = api_class.post(
                        api_class.session, api_class.base_url + constants.FEATURE_PATH,
                        data=json.dumps(fd)
                    )
                    new_template_id = post_response.data[constants.TEMPLATE_ID]
                template_id_mapping[template_id] = new_template_id
        new_device_template = copy.deepcopy(device_template)
        for feature in new_device_template[constants.GENERAL_TEMPLATES]:
            feature[constants.TEMPLATE_ID] = template_id_mapping[feature[constants.TEMPLATE_ID]]
            if constants.SUB_TEMPLATES in feature:
                for sub_temp in feature[constants.SUB_TEMPLATES]:
                    if constants.SUB_TEMPLATES in sub_temp:
                        for template in sub_temp[constants.SUB_TEMPLATES]:
                            template[constants.TEMPLATE_ID] = template_id_mapping[
                                template[constants.TEMPLATE_ID]
                            ]
                    sub_temp[constants.TEMPLATE_ID] = template_id_mapping[
                        sub_temp[constants.TEMPLATE_ID]
                    ]
        if constants.UID_RANGE in new_device_template and new_device_template.get(
                constants.UID_RANGE):
            for add_template in new_device_template[constants.UID_RANGE]:
                add_template[constants.TEMPLATE_ID] = template_id_mapping[
                    add_template[constants.TEMPLATE_ID]
                ]
        if constants.POLICY_ID in device_template and device_template[constants.POLICY_ID]:
            policy_data = template_dict.get(
                '{}_policy'.format(device_template[constants.TEMPLATE_NAME])
            )
            policy_id = device_template[constants.POLICY_ID]
            if policy_id not in policy_data:
                # logger.debug('Policy data missing in source templates.')
                pass
            pd = policy_data[policy_id]
            ch = check_policy(pd[constants.POLICY_NAME])
            if ch is False:
                pd = {k: v for k, v in pd.items() if k in constants.POLICY_KEYS}
                _ = api_class.post(
                    api_class.session, api_class.base_url + constants.VEDGE_POLICY_PATH,
                    data=json.dumps(pd)
                )
                new_policy_id = check_policy(pd[constants.POLICY_NAME])
            else:
                new_policy_id = ch
            new_device_template[constants.POLICY_ID] = new_policy_id
        new_device_template = {
            k: v for k, v in new_device_template.items() if k in constants.DEVICE_TEMPLATE_KEYS
        }
        check_device = False
        for device in api_class.get(
                api_class.session, api_class.base_url + constants.DEVICE_PATH
        ).data:
            if device[constants.TEMPLATE_NAME] == new_device_template[constants.TEMPLATE_NAME]:
                check_device = True
                break
        if not check_device:
            _ = api_class.post(
                api_class.session, api_class.base_url + constants.DEVICE_FEATURE_PATH,
                data=json.dumps(new_device_template)
            )
        else:
            # TODO: Logging here
            # logger.debug('Skipping {}'.format(new_device_template[constants.TEMPLATE_NAME]))
            pass
