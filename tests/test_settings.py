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
    mock_resource_filename.return_value = 'tests/foo_no_secrets_doc.yml'
    settings.init('loadtests.foo.locustfile', ['REQUIRED_KEY'])
    with open('tests/foo_no_secrets_doc.yml') as foo:
        settings_documents = yaml.load_all(foo)
        foo_data = settings_documents.next()
        with pytest.raises(StopIteration):
            settings_documents.next()
    assert settings.data == foo_data
    assert settings.secrets == {}


@pytest.mark.usefixtures("reset_settings")
@patch('helpers.settings.resource_filename')
def test_load_settings_empty_secrets(mock_resource_filename):
    """
    load a valid settings file with an empty "secrets" yaml document.
    """
    mock_resource_filename.return_value = 'tests/foo_empty_secrets_doc.yml'
    settings.init('loadtests.foo.locustfile', ['REQUIRED_KEY'])
    with open('tests/foo_empty_secrets_doc.yml') as foo:
        foo_data, foo_secrets = yaml.load_all(foo)
    assert settings.data == foo_data
    assert settings.secrets == {}
    assert foo_secrets is None


def test_settings_generic():
    """
    Settings class smoke tests.
    """
    empty_settings = settings.Settings()
    sparse_settings = settings.Settings({'public_settings_key': 1}, {'secret_settings_key': 2})

    # Make sure that we start out with a blank slate when called without
    # constructor parameters:
    assert isinstance(empty_settings.data, dict) and not empty_settings.data
    assert isinstance(empty_settings.secrets, dict) and not empty_settings.secrets

    # Validation tests.
    empty_settings.validate_required()
    sparse_settings.validate_required()
    sparse_settings.validate_required(['public_settings_key'])
    with pytest.raises(settings.MissingRequiredSettingError):
        empty_settings.validate_required(['missing_settings_key'])
    with pytest.raises(settings.MissingRequiredSettingError):
        empty_settings.validate_required(required_secrets=['missing_secret_settings_key'])
    with pytest.raises(settings.MissingRequiredSettingError):
        sparse_settings.validate_required(['missing_settings_key'])

    # Make sure the .data attribute is actually protected:
    try:
        # Try to set the protected data attribute.
        test_settings.data = {'foo': 'bar'}
    except:
        # Implementation dictates whether or not this is an error, but in this
        # test we don't care.
        pass
    else:
        # If there was no error, still make sure it was not changed.
        assert not test_settings.data


def test_settings_equality():
    settings1 = settings.Settings(
        data={
            'a': 3,
            'b': 3,
        },
        secrets={
            'c': 3,
            'd': 3,
        },
    )
    settings2 = settings.Settings(
        data={
            'a': 3,
            'b': 3,
        },
        secrets={
            'c': 3,
            'd': 3,
        },
    )
    settings3 = settings.Settings(
        data={
            'a': 1,
            'b': 3,
        },
        secrets={
            'c': 3,
            'd': 3,
        },
    )
    settings4 = settings.Settings(
        data={
            'a': 1,
            'b': 3,
        },
    )
    assert settings1 == settings1
    assert settings1 == settings2
    assert settings1 != settings3
    assert settings1 != settings4
    assert settings2 == settings2
    assert settings2 != settings3
    assert settings2 != settings4
    assert settings3 == settings3
    assert settings3 != settings4


def test_settings_update():
    """
    Settings.update() test to make sure overrides are working properly, keys
    don't get dropped, etc.
    """
    test_settings = settings.Settings(
        data={
            'key_from_file_1': 1,
            'key_from_file_1_overridden': 1,
        },
    )
    test_settings.update(settings.Settings(
        secrets={
            'secret_key_from_file_2': 2,
            'secret_key_from_file_2_overridden': 2,
        },
    ))
    test_settings.update(settings.Settings(
        data={
            'key_from_file_1_overridden': 3,
            'key_from_file_3': 3,
        },
        secrets={
            'secret_key_from_file_2_overridden': 3,
            'secret_key_from_file_3': 3,
        },
    ))
    expected_settings = settings.Settings(
        data={
            'key_from_file_1': 1,
            'key_from_file_1_overridden': 3,
            'key_from_file_3': 3,
        },
        secrets={
            'secret_key_from_file_2': 2,
            'secret_key_from_file_2_overridden': 3,
            'secret_key_from_file_3': 3,
        },
    )
    # Settings implements __eq__() so assume this is actually doing the right
    # thing.
    assert test_settings == expected_settings
