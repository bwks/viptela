"""Constants used by the Viptela module."""


# Misc commonly used keys and constants.
CONFIG = 'config'
CONSTANT = 'constant'
DATA = 'data'
DEVICE_MODELS = 'deviceModels'
ERROR = 'error'
FALSE = 'false'
IGNORE = 'ignore'
TRUE = 'true'
V_15 = '15.0.0'
VARIABLE = 'variable'

# Keys used in interacting with templates.
DEVICE_TYPE = 'deviceType'
FACTORY_DEFAULT = 'factoryDefault'
GENERAL_TEMPLATES = 'generalTemplates'
POLICY_DEFINITION = 'policyDefinition'
POLICY_DESCRIPTION = 'policyDescription'
POLICY_NAME = 'policyName'
POLICY_ID = 'policyId'
SUB_TEMPLATES = 'subTemplates'
TEMPLATE_DEFINITION = 'templateDefinition'
TEMPLATE_DESCRIPTION = 'templateDescription'
TEMPLATE_ID = 'templateId'
TEMPLATE_MIN_VERSION = 'templateMinVersion'
TEMPLATE_NAME = 'templateName'
TEMPLATE_TYPE = 'templateType'
UID_RANGE = 'featureTemplateUidRange'
FEATURE_KEYS = [
    TEMPLATE_NAME,
    TEMPLATE_DESCRIPTION,
    TEMPLATE_TYPE,
    TEMPLATE_MIN_VERSION,
    DEVICE_TYPE,
    FACTORY_DEFAULT,
    TEMPLATE_DEFINITION
]
POLICY_KEYS = [
    POLICY_NAME,
    POLICY_DESCRIPTION,
    POLICY_DEFINITION
]
DEVICE_TEMPLATE_KEYS = [
    TEMPLATE_NAME,
    TEMPLATE_DESCRIPTION,
    'deviceType',
    'configType',
    'factoryDefault',
    POLICY_ID,
    UID_RANGE,
    GENERAL_TEMPLATES
]

# Constants used for interacting with HTTP methods.
STANDARD_JSON_HEADER = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}
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
HTTP_RESPONSE_CODES = {k: v for d in (HTTP_SUCCESS_CODES, HTTP_ERROR_CODES) for k, v in d.items()}

# Various structures containing device model data.
VEDGE = 'vedge'
VSMART = 'vsmart'
DEVICE_MODEL_MAP = {
    'vedge-cloud': {'name': 'vedge-cloud', 'displayName':'vEdge Cloud', 'deviceType': VEDGE},
    'vedge-100': {'name': 'vedge-100', 'displayName': 'vEdge 100', 'deviceType': VEDGE},
    'vedge-100-B': {'name': 'vedge-100-B', 'displayName': 'vEdge 100 B', 'deviceType': VEDGE},
    'vedge-100-M': {'name': 'vedge-100-M', 'displayName': 'vEdge 100 M', 'deviceType': VEDGE},
    'vedge-100-WM': {'name': 'vedge-100-WM', 'displayName': 'vEdge 100 WM', 'deviceType': VEDGE},
    'vedge-1000': {'name': 'vedge-1000', 'displayName': 'vEdge 1000', 'deviceType': VEDGE},
    'vedge-2000': {'name': 'vedge-2000', 'displayName': 'vEdge 2000', 'deviceType': VEDGE},
    'vmanage': {'name': 'vmanage', 'displayName': 'vManage', 'deviceType': 'vmanage'},
    VSMART: {'name': 'vsmart', 'displayName': 'vSmart', 'deviceType': VSMART},
}
ALL_DEVICE_TYPES = tuple(DEVICE_MODEL_MAP.keys())
ALL_DEVICE_MODELS = tuple(DEVICE_MODEL_MAP.values())


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
BASE_POLICY_PATH = _TEMPLATE + 'policy/'
VEDGE_POLICY_PATH = BASE_POLICY_PATH + VEDGE
VSMART_POLICY_PATH = BASE_POLICY_PATH + VSMART
