import os

from lms.envs.common import *

XQUEUE_INTERFACE = {}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': None,
        'NAME': 'wwc',
        'PASSWORD': None,
        'PORT': '3306',
        'USER': None
    }
}

DATABASES['default'].update(
    {k: os.environ.get('DB_' + k)
        for k in ['ENGINE', 'HOST', 'NAME', 'PASSWORD', 'PORT', 'USER']
        if 'DB_' + k in os.environ})
