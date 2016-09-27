import os
import yaml
import logging
from pkg_resources import resource_filename
from pprint import pformat

LOG = logging.getLogger(__name__)
data = None


def init(test_module_full_name, required=[]):
    """
    This initializes the global settings_dict, and loads settings from the
    correct settings file.  To use this module for your load tests, include the
    following two lines in your locustfile.py:

      from helpers import settings
      settings.init(__name__)

    Then, create a settings file: "settings_files/<TEST MODULE NAME>.yml"

    Anywhere you need to use the settings data, make sure the settings module
    is imported, then use:

      settings.data['SOMETHING']

    """
    global data
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
        data = yaml.load(settings_file)
    LOG.info('loaded the following settings:\n{}'.format(pformat(data)))

    # check that the required keys are present
    for key in required:
        if data.get(key) is None:
            raise RuntimeError(
                'the {} parameter is required for {} load tests.'.format(
                    key,
                    test_module_name,
                )
            )
