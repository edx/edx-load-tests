from __future__ import print_function
import os
import os.path
from paver.easy import task, sh, cmdopts
from optparse import make_option

# tests are located under this directory
SETTINGS_DIR = 'settings_files'

# list of valid environments:
VALID_ENVIRONMENTS = [
    'loadtest',  # aka courses-loadtest.edx.org
    'sandbox',
    'devstack',
]


def get_desired_settings_file(loadtest):
    """create path to desired settings file"""
    return '{}/{}.yml'.format(SETTINGS_DIR, loadtest)


def get_example_settings_file(loadtest, environment):
    """create path to example settings file"""
    if environment not in VALID_ENVIRONMENTS:
        raise RuntimeError(
            'not a valid environment: "{}".  should be one of {}'.format(
                environment,
                VALID_ENVIRONMENTS,
            )
        )
    desired = get_desired_settings_file(loadtest)
    example_settings = None
    if environment == 'loadtest':
        example_settings = '{}.example'.format(desired)
    else:
        example_settings = '{}.{}-example'.format(desired, environment)
    if not os.path.isfile(example_settings):
        raise RuntimeError(
            'could not find example settings file {}'.format(example_settings)
        )
    return example_settings


@task
@cmdopts([
    make_option(
        '-n', '--loadtest-name', type='string',
        help='the name of the loadtests to setup (REQUIRED)'),
    make_option(
        '-e', '--environment', type='string', default='loadtest',
        help='the target environment for which to choose settings'),
    make_option(
        '-f', '--force', action='store_true', default=False,
        help='force the overwrite of pre-existing settings'),
])
def settings(options):
    """ensure a settings file is present"""
    # NOTE: Some tests may not implement helpers.settings.  Those tests are not
    # supported by this task.

    # There no way in paver to make an option required.  There's also no way to
    # mix positional arguments with optional arguments without introducing our
    # own argument parser.  Here we manually gate for required options:
    if options.get('loadtest_name') is None:
        raise RuntimeError('missing required option: --loadtest-name=')

    desired_settings = get_desired_settings_file(options.loadtest_name)
    example_settings = \
        get_example_settings_file(options.loadtest_name, options.environment)

    # only write settings if it doesn't already exist, or --force is supplied
    if not os.path.isfile(desired_settings) or options.force:
        # use /bin/cp instead of, e.g., shutil.copyfile because the output is
        # clearer this way.
        sh('cp {} {}'.format(example_settings, desired_settings))

    print('NOTICE: settings for the {} load test can be changed by modifying\n'
          'the following file:\n'
          '\n'
          '  {}\n'.format(options.loadtest_name, desired_settings))
