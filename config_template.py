LOG_LEVEL = 'INFO' # CRITICAL, ERROR, WARNING, INFO, DEBUG (more output)
LOG_FILE = 'github_youtrack_hook.log'
LOG_ROTATE_PERIOD = 'h' # mignight, h, m
LOG_ROTATE_INTERVAL = 24 # works with 'h', 'm'
LOG_ROTATE_BACKUP_COUNT = 7 # backup files count

WEBHOOK_ENDPOINT = '/postreceive'
WEBHOOK_SECRET = '<REQUIRED>'

LDAP_EMAIL_DOMAIN = '<REQUIRED>' # including '@': '@example.com'
LDAP_LOGIN_INCLUDES_EMAIL = False

DEFAULT_FIX_VERSIONS_REGEX = 'release_(\d+)_(\d+)'
DEFAULT_YOUTRACK_URL = '<REQUIRED>'
DEFAULT_YOUTRACK_USER = '<REQUIRED>'
DEFAULT_YOUTRACK_PASS = '<REQUIRED>'
ALLOWED_YOUTRACK_PROJECTS = {'<REQUIRED_GITHUB_FULL_NAME>':['<REQUIRED>','<REQUIRED>']} # key = ex. 'cuba-platform/cuba', value = list of comma separated projects

COMMITTED_BRANCHES_FIELD = "Committed to"
FIX_VERSIONS_FIELD = "Fix versions"

DEFAULT_GIT_ISSUE_NUMBER_MASKS = [
    '([A-Z][A-Z0-9_]*-\d+)',
    '#(\w+-\d+)'
]

DEFAULT_GIT_RELEASE_BRANCH_MASKS = [
    'release_(\d+)_(\d+)$',
    'master$'
]

DEFAULT_GITHUB_URL = 'https://github.com/%s/commit/%s'
