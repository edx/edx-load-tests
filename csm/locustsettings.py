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
    },
    'student_module_history': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': None,
        'NAME': 'edxapp',
        'PASSWORD': None,
        'PORT': '3306',
        'USER': None
    }
}

DATABASES['default'].update(
    {k: os.environ.get('DB_' + k)
        for k in ['ENGINE', 'HOST', 'NAME', 'PASSWORD', 'PORT', 'USER']
        if 'DB_' + k in os.environ})

DATABASES['student_module_history'].update(
    {k: os.environ.get('CSMH_DB_' + k)
        for k in ['ENGINE', 'HOST', 'NAME', 'PASSWORD', 'PORT', 'USER']
        if 'DB_' + k in os.environ})

