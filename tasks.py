import os
from invoke import task


def get_desired_settings_file(ctx, loadtest):
    """create path to desired settings file"""
    return '{}/{}.yml'.format(ctx['settings_dir'], loadtest)


def get_example_settings_file(ctx, loadtest, environment):
    """create path to example settings file"""
    if environment not in ctx['environments']:
        raise RuntimeError(
            'not a valid environment: "{}".  should be one of {}'.format(
                environment,
                ctx['environments'],
            )
        )
    desired = get_desired_settings_file(ctx, loadtest)
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
def settings(ctx, loadtest_name, environment='loadtest', force=False):
    """ensure a settings file is present"""
    # NOTE: Some tests may not implement helpers.settings.  Those tests are not
    # supported by this task.

    desired_settings = get_desired_settings_file(ctx, loadtest_name)
    example_settings = get_example_settings_file(ctx, loadtest_name, environment)

    # only write settings if it doesn't already exist, or --force is supplied
    if not os.path.isfile(desired_settings) or force:
        ctx.run('cp {} {}'.format(example_settings, desired_settings))

    print 'NOTICE: Settings for the {} load test can be changed by modifying\n' \
          'the following file:\n' \
          '\n' \
          '  {}\n'.format(loadtest_name, desired_settings)
