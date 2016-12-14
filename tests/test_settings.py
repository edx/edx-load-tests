"""test functions in helpers.settings"""

import pytest
from mock import patch
import yaml
from helpers import settings


@pytest.fixture(scope='function')
def reset_settings():
    """
    This is a baseline for all settings-related tests.  It clears any
    settings-related state that have been setup by prior tests.
    """
    settings.data = None
    settings.secrets = None


@pytest.mark.usefixtures("reset_settings")
@patch('helpers.settings.resource_filename')
def test_load_settings(mock_resource_filename):
    """
    normal successful circumstances: load a valid settings file with a mix of
    optional/required/public/secret settings.
    """
    mock_resource_filename.return_value = 'tests/foo.yml'
    settings.init('loadtests.foo.locustfile', ['REQUIRED_KEY'], ['REQUIRED_SECRET_KEY'])
    mock_resource_filename.assert_called_once_with('settings_files', 'foo.yml')
    with open('tests/foo.yml') as foo:
        foo_data, foo_secrets = yaml.load_all(foo)
    assert settings.data == foo_data
    assert settings.secrets == foo_secrets


@pytest.mark.usefixtures("reset_settings")
@patch('helpers.settings.resource_filename')
def test_load_settings_missing_required_data(mock_resource_filename):
    """
    missing required setting in main document should raise an exception
    """
    mock_resource_filename.return_value = 'tests/foo.yml'

    with pytest.raises(settings.MissingRequiredSettingError):
        settings.init('loadtests.foo.locustfile', required_data=['MISSING_REQUIRED_KEY'])


@pytest.mark.usefixtures("reset_settings")
@patch('helpers.settings.resource_filename')
def test_load_settings_missing_required_secrets(mock_resource_filename):
    """
    missing required setting in secrets document should raise an exception
    """
    mock_resource_filename.return_value = 'tests/foo.yml'

    with pytest.raises(settings.MissingRequiredSettingError):
        settings.init('loadtests.foo.locustfile', required_secrets=['MISSING_REQUIRED_KEY'])


@pytest.mark.usefixtures("reset_settings")
@patch('helpers.settings.resource_filename')
def test_load_settings_no_secrets(mock_resource_filename):
    """
    load a valid settings file without a "secrets" yaml document.
    """
    mock_resource_filename.return_value = 'tests/foo_no_secrets.yml'
    settings.init('loadtests.foo.locustfile', ['REQUIRED_KEY'])
    with open('tests/foo_no_secrets.yml') as foo:
        settings_documents = yaml.load_all(foo)
        foo_data = settings_documents.next()
        with pytest.raises(StopIteration):
            settings_documents.next()
    assert settings.data == foo_data
    assert settings.secrets == {}
