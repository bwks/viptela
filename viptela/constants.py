"""Constants used by the Viptela module."""


# Misc commonly used keys and constants.
CONFIG = 'config'
CONSTANT = 'constant'
DATA = 'data'
DEVICE_MODELS = 'deviceModels'
ERROR = 'error'
FALSE = 'false'
IGNORE = 'ignore'
JSON_EXT = '.json'
NAME = 'name'
PRIORITY_ORDER = 'priority-order'
PROTOCOL = 'protocol'
TREE = 'tree'
TRUE = 'true'
V_15 = '15.0.0'
VARIABLE = 'variable'
VIP_OBJECT_TYPE = 'vipObjectType'
VIP_PRIMARY_KEY = 'vipPrimaryKey'
VIP_TYPE = 'vipType'
VIP_VALUE = 'vipValue'

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
    DEVICE_TYPE,
    'configType',
    FACTORY_DEFAULT,
    POLICY_ID,
    UID_RANGE,
    GENERAL_TEMPLATES
]

# Constants used for interacting with HTTP methods.
STANDARD_HTTP_TIMEOUT = 10
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
DISPLAY_NAME = 'displayName'
VEDGE = 'vedge'
VEDGE_100 = 'vedge-100'
VEDGE_100B = 'vedge-100-B'
VEDGE_100M = 'vedge-100-M'
VEDGE_100WM = 'vedge-100-WM'
VEDGE_1000 = 'vedge-1000'
VEDGE_2000 = 'vedge-2000'
VEDGE_CLOUD = 'vedge-cloud'
VMANAGE = 'vmanage'
VSMART = 'vsmart'
DEVICE_MODEL_MAP = {
    VEDGE_CLOUD: {NAME: VEDGE_CLOUD, DISPLAY_NAME: 'vEdge Cloud', DEVICE_TYPE: VEDGE},
    VEDGE_100: {NAME: VEDGE_100, DISPLAY_NAME: 'vEdge 100', DEVICE_TYPE: VEDGE},
    VEDGE_100B: {NAME: VEDGE_100B, DISPLAY_NAME: 'vEdge 100 B', DEVICE_TYPE: VEDGE},
    VEDGE_100M: {NAME: VEDGE_100M, DISPLAY_NAME: 'vEdge 100 M', DEVICE_TYPE: VEDGE},
    VEDGE_100WM: {NAME: VEDGE_100WM, DISPLAY_NAME: 'vEdge 100 WM', DEVICE_TYPE: VEDGE},
    VEDGE_1000: {NAME: VEDGE_1000, DISPLAY_NAME: 'vEdge 1000', DEVICE_TYPE: VEDGE},
    VEDGE_2000: {NAME: VEDGE_2000, DISPLAY_NAME: 'vEdge 2000', DEVICE_TYPE: VEDGE},
    VMANAGE: {NAME: VMANAGE, DISPLAY_NAME: 'vManage', DEVICE_TYPE: VMANAGE},
    VSMART: {NAME: VSMART, DISPLAY_NAME: 'vSmart', DEVICE_TYPE: VSMART},
}
ALL_DEVICE_TYPES = tuple(DEVICE_MODEL_MAP.keys())
ALL_DEVICE_MODELS = tuple(DEVICE_MODEL_MAP.values())


# Strings used for building URL paths.
_DEVICE = 'device/'
_FEATURE = 'feature/'
_TEMPLATE = '/template/'

# URL paths used in interacting with the API.
BANNER_PATH_W_BASE = '{0}/settings/configuration/banner'
BASE_TEMPLATE_PATH_W_BASE = '{0}/template/feature'
DEVICE_PATH = _TEMPLATE + _DEVICE
DEVICE_FEATURE_PATH = _TEMPLATE + _DEVICE + _FEATURE
FEATURE_PATH = _TEMPLATE + _FEATURE
BASE_POLICY_PATH = _TEMPLATE + 'policy/'
VEDGE_POLICY_PATH = BASE_POLICY_PATH + VEDGE
VSMART_POLICY_PATH = BASE_POLICY_PATH + VSMART
VSMART_POLICY_PATH_W_BASE = '{0}' + VSMART_POLICY_PATH
