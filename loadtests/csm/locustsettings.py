# imports from the "lms" module in edx-platform, not the lms load tests
from lms.envs.common import *

# get parameters from the *test* settings file (settings_files/csm.yml)
from helpers import settings

XQUEUE_INTERFACE = {}

DATABASES = {}

# set the database parameters using "DB_" prefixed settings
DATABASES['default'] = {
    k: settings.data['DB_{}'.format(k)]
    for k in ['ENGINE', 'HOST', 'NAME', 'PASSWORD', 'PORT', 'USER']
    if 'DB_{}'.format(k) in settings.data.keys()
}
