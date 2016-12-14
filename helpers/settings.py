"""
This module helps manage settings files.  To use this module for your load
tests:

1. Include the following two lines in your locustfile.py:

     from helpers import settings
     settings.init(__name__)

2. Create a settings file: "settings_files/<TEST MODULE NAME>.yml"

   We assume the first yaml document contains non-secret settings, and the
   second document contains secrets.  The second yaml document is optional.

   Example settings file:

     ---
     hello: world
     ---
     # secrets
     password: set-me
     ...

3. Anywhere you need to use the settings data, make sure the settings module
   is imported, then use:

     settings.data['hello']  # returns 'world'

   or:

     settings.secrets['password']  # returns 'set-me'

"""
import os
import yaml
import logging
from pkg_resources import resource_filename
from pprint import pformat

LOG = logging.getLogger(__name__)
data = None
secrets = None


class MissingRequiredSettingError(Exception):
    pass


def init(test_module_full_name, required_data=[], required_secrets=[]):
    """
    This is the primary entrypoint for this module.  In short, it initializes
    the global data dict, finds/loads the settings files, and validates the
    data.
    """
    global data
    global secrets
    if data is not None:
        raise RuntimeError('helpers.settings has been initialized twice!')

    # Find the correct settings file under the "settings_files" directory of
    # this package.  The name of the settings file corresponds to the
    # name of the directory containing the locustfile. E.g.
    # "loadtests/lms/locustfile.py" reads settings data from
    # "settings_files/lms.yml".
    test_module_name = test_module_full_name.split('.')[-2]
    settings_filename = \
        resource_filename('settings_files', '{}.yml'.format(test_module_name))
    settings_filename = os.path.abspath(settings_filename)
    LOG.info('using settings file: {}'.format(settings_filename))

    # load the settings file
    with open(settings_filename, 'r') as settings_file:
        settings_documents = yaml.load_all(settings_file)
        data = settings_documents.next()
        try:
            secrets = settings_documents.next()
        except StopIteration:
            secrets = {}
    if len(secrets) > 0:
        LOG.info('secrets loaded from the settings file')
    else:
        LOG.info('no secrets were specified in the settings file')
    LOG.info('loaded the following public settings:\n{}'.format(
        pformat(data),
    ))

    # check that the required settings are present
    for key in required_data:
        if data.get(key) is None:
            raise MissingRequiredSettingError(
                'the setting {} is absent, but required for the {} load tests.'.format(
                    key,
                    test_module_name,
                )
            )

    # check that the required secrets are present
    for key in required_secrets:
        if secrets.get(key) is None:
            raise MissingRequiredSettingError(
                'the secret setting {} is absent, but required for the {} load tests.'.format(
                    key,
                    test_module_name,
                )
            )
