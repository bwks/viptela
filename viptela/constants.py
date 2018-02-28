"""Constants used by the Viptela module."""


# Strings used for building URL paths.
_DEVICE = 'device/'
_FEATURE = 'feature/'
_TEMPLATE = '/template/'

# URL paths used in interacting with the API.
BANNER_PATH = '{0}/settings/configuration/banner'
BASE_TEMPLATE_PATH = '{0}/template/feature'
DEVICE_PATH = _TEMPLATE + _DEVICE
DEVICE_FEATURE_PATH = _TEMPLATE + _DEVICE + _FEATURE
FEATURE_PATH = _TEMPLATE + _FEATURE
VEDGE_POLICY_PATH = _TEMPLATE + 'policy/vedge/'

# Misc commonly used constants.
STANDARD_JSON_HEADER = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}

# Misc commonly used keys.
CONFIG = 'config'
DATA = 'data'
ERROR = 'error'
TEMPLATE_DEFINITION = 'templateDefinition'

# Keys used in interacting with templates.
GENERAL_TEMPLATES = 'generalTemplates'
POLICY_NAME = 'policyName'
POLICY_ID = 'policyId'
SUB_TEMPLATES = 'subTemplates'
TEMPLATE_ID = 'templateId'
TEMPLATE_NAME = 'templateName'
UID_RANGE = 'featureTemplateUidRange'

FEATURE_KEYS = [
    TEMPLATE_NAME,
    'templateDescription',
    'templateType',
    'templateMinVersion',
    'deviceType',
    'factoryDefault',
    'templateDefinition'
]

POLICY_KEYS = [
    POLICY_NAME,
    'policyDescription',
    'policyDefinition'
]

DEVICE_TEMPLATE_KEYS = [
    TEMPLATE_NAME,
    'templateDescription',
    'deviceType',
    'configType',
    'factoryDefault',
    POLICY_ID,
    UID_RANGE,
    GENERAL_TEMPLATES
]