# -*- coding: utf-8 -*-

IP_ADDRESS = '0.0.0.0'
PORT = '8080'

LOG_LEVEL = 'INFO'  # CRITICAL, ERROR, WARNING, INFO, DEBUG (more output)
LOG_FILE = 'github_youtrack_hook.log'
LOG_ROTATE_PERIOD = 'h'  # midnight, h, m
LOG_ROTATE_INTERVAL = 24  # works with 'h', 'm'
LOG_ROTATE_BACKUP_COUNT = 7  # backup files count

WEBHOOK_ENDPOINT = '/postreceive'
WEBHOOK_SECRET = '<REQUIRED>'

LDAP_EMAIL_DOMAIN = '<REQUIRED>'  # including '@': '@example.com'
LDAP_LOGIN_INCLUDES_EMAIL = False

DEFAULT_FIX_VERSIONS_REGEX = 'release_(\d+)_(\d+)'
DEFAULT_YOUTRACK_URL = '<REQUIRED>'
DEFAULT_YOUTRACK_USER = '<REQUIRED>'
DEFAULT_YOUTRACK_PASS = '<REQUIRED>'

YOUTRACK_PROJECTS = {
    "<REQUIRED>": {  # allowed YouTrack PROJECT-1
        "COMMITTED_TO": "Committed to",  # YouTrack custom field-1
        "FIX_VERSIONS": "Fix versions",  # YouTrack custom field-2
        "GITHUB_PROJECTS": ["<REQUIRED_GITHUB_FULL_NAME>"]  # ex. "cuba-platform/cuba"
    },
    "<REQUIRED>": {  # allowed YouTrack PROJECT-n
        "COMMITTED_TO": "Committed to",
        "FIX_VERSIONS": "Fix versions",
        "GITHUB_PROJECTS": ["<REQUIRED_GITHUB_FULL_NAME>"]  # ex. "cuba-platform/cuba-gradle-plugin"
    }
}

DEFAULT_GIT_ISSUE_NUMBER_MASKS = [
    '([A-Z][A-Z0-9_]*-\d+)',
    '#(\w+-\d+)'
]

DEFAULT_GIT_RELEASE_BRANCH_MASKS = [
    'release_(\d+)_(\d+)$',
    'master$'
]

DEFAULT_GITHUB_URL = 'https://github.com/%s/commit/%s'
