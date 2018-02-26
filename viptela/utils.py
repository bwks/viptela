"""
Various utilities and helper functions that are implement commonly used features and processes.
"""


import copy
import os
import json


def create_template_dict(template_dir):
    """Create a dict containing all of the JSON from a template directory for the vManage server."""
    if not template_dir.endswith('/'):
        template_dir += '/'
    template_dict = {}
    json_files = [f for f in os.listdir(template_dir) if f.endswith('.json')]
    for file in json_files:
        with open(template_dir + file) as f:
            raw_file = f.read()
        template_dict[file.split('.json')[0]] = json.loads(raw_file)
    return template_dict


def import_provisioning_templates(api_class, template_dict):
    """Import templates from into the vManage server."""

    def check_policy(policy_name):
        return_data = api_class.get(
            api_class.session, api_class.base_url + '/template/policy/vedge/'
        ).data
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
                feature_template_id_map_data = api_class.get(
                    api_class.session, api_class.base_url + '/template/feature'
                ).data
                feature_template_id_map = {
                    k['templateName']: k['templateId'] for k in feature_template_id_map_data
                }
                if fd['templateName'] in feature_template_id_map:
                    new_template_id = feature_template_id_map[fd['templateName']]
                else:
                    post_response = api_class.post(
                        api_class.session, api_class.base_url + '/template/feature',
                        data=json.dumps(fd)
                    )
                    new_template_id = post_response.data['templateId']
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
                pd = {k: v for k, v in pd.items() if k in policy_keys}
                _ = api_class.post(
                    api_class.session, api_class.base_url + '/template/policy/vedge/',
                    data=json.dumps(pd)
                )
                new_policy_id = check_policy(pd['policyName'])
            else:
                new_policy_id = ch
            new_device_template['policyId'] = new_policy_id
        new_device_template = {
            k: v for k, v in new_device_template.items() if k in device_template_keys
        }
        check_device = False
        for device in api_class.get(
                api_class.session, api_class.base_url + '/template/device'
        ).data:
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
