import os
import os.path
import sys
from paver.easy import task, sh, cmdopts, consume_args, call_task
import argparse

# settings are located under this directory
SETTINGS_DIR = 'settings_files'

# tests are located under this directory
LOADTESTS_DIR = 'loadtests'

# list of valid environments:
VALID_ENVIRONMENTS = [
    'loadtest',  # aka courses-loadtest.edx.org
    'sandbox',
    'devstack',
]


def validate_environment(environment):
    if environment not in VALID_ENVIRONMENTS:
        raise RuntimeError(
            'not a valid environment: "{}".  should be one of {}'.format(
                environment,
                VALID_ENVIRONMENTS,
            )
        )


def validate_loadtest(loadtest):
    all_loadtests = [
        dirname for dirname in os.listdir(LOADTESTS_DIR)
        if os.path.isdir(os.path.join(LOADTESTS_DIR, dirname))
    ]
    if loadtest not in all_loadtests:
        raise RuntimeError(
            'not a valid loadtest name: "{}".  should be one of {}'.format(
                loadtest,
                all_loadtests,
            )
        )


def get_desired_settings_file(loadtest):
    """create path to desired settings file"""
    return '{}/{}.yml'.format(SETTINGS_DIR, loadtest)


def get_example_settings_file(loadtest, environment):
    """create path to example settings file"""
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
    ('loadtest-name=', 'n', 'the name of the loadtests to setup (REQUIRED)'),
    ('environment=', 'e', 'the target environment for which to choose settings'),
    ('force', 'f', 'force the overwrite of pre-existing settings'),
])
def settings(options):
    """ensure a settings file is present"""
    # NOTE: Some tests may not implement helpers.settings.  Those tests are not
    # supported by this task.

    # There no way in paver to make an option required.  There's also no way to
    # mix positional arguments with optional arguments without introducing our
    # own argument parser.  Here we manually gate for required options:
    if not hasattr(options, 'loadtest_name'):
        raise RuntimeError('missing required option: --loadtest-name=')

    # collect all the options and set defaults
    loadtest_name = getattr(options, 'loadtest_name')  # required, no default
    environment = getattr(options, 'environment', 'loadtest')
    force = hasattr(options, 'force')  # value of option is irrelevant

    # input validation
    validate_environment(environment)
    validate_loadtest(loadtest_name)

    desired_settings = get_desired_settings_file(loadtest_name)
    example_settings = get_example_settings_file(loadtest_name, environment)

    if not os.path.isfile(desired_settings) or force:
        # use /bin/cp instead of, e.g., shutil.copyfile because the output is
        # clearer this way.
        sh('cp {} {}'.format(example_settings, desired_settings))
    else:
        print('Not overwriting settings file.')

    print('NOTICE: settings for the {} load test can be changed by modifying\n'
          'the following file:\n'
          '\n'
          '  {}\n'.format(loadtest_name, desired_settings))


@task
@consume_args
def loadtest(args):
    """run a specified load test"""
    # look for the special "--" divider.  LHS corresponds to the task, RHS
    # corresponds to locust passthrough options.
    if '--' in args:
        task_args = args[:args.index('--')]
        extra_locust_args = args[args.index('--') + 1:]
    else:
        task_args = args
        extra_locust_args = []

    # we need to use our own argument parser because of the presence of locust
    # passthrough options.
    parser = argparse.ArgumentParser(prog='paver loadtest')
    parser.add_argument('-n', '--loadtest-name', help='the name of the loadtest to run (REQUIRED)')
    task_options = parser.parse_args(task_args)
    if not hasattr(task_options, 'loadtest_name'):
        raise RuntimeError('missing required option: --loadtest-name=')

    loadtest_name = task_options.loadtest_name

    # input validation
    validate_loadtest(loadtest_name)

    # ensure there is a settings file to use
    call_task('settings', options={'loadtest_name': loadtest_name})

    # this task is terminal and long-running.  leave paver behind, and execvp
    # straight into locust.
    sys.stdout.flush()
    sys.stderr.flush()
    os.execvp('locust', ['locust', '--locustfile=loadtests/{}'.format(loadtest_name)] + extra_locust_args)
