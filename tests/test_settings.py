"""test functions in helpers.settings"""

import unittest
from mock import patch
import yaml
from helpers import settings


class TestSettingsModule(unittest.TestCase):

    def _reset_settings(self):
        settings.data = None
        settings.secrets = None

    @patch('helpers.settings.resource_filename')
    def test_load_settings(self, mock_resource_filename):
        mock_resource_filename.return_value = 'tests/foo.yml'
        settings.init('loadtests.foo.locustfile', ['REQUIRED_KEY'], ['REQUIRED_SECRET_KEY'])
        mock_resource_filename.assert_called_once_with('settings_files', 'foo.yml')
        with open('tests/foo.yml') as foo:
            foo_data, foo_secrets = yaml.load_all(foo)
        assert settings.data == foo_data
        assert settings.secrets == foo_secrets
        self._reset_settings()

    @patch('helpers.settings.resource_filename')
    def test_load_settings_missing_requirements(self, mock_resource_filename):
        mock_resource_filename.return_value = 'tests/foo.yml'

        # test missing setting in main document
        with self.assertRaises(settings.MissingRequiredSettingError):
            settings.init('loadtests.foo.locustfile', required=['MISSING_REQUIRED_KEY'])
        self._reset_settings()

        # test missing setting in secrets document
        with self.assertRaises(settings.MissingRequiredSettingError):
            settings.init('loadtests.foo.locustfile', secrets_required=['MISSING_REQUIRED_KEY'])
        self._reset_settings()

    @patch('helpers.settings.resource_filename')
    def test_load_settings_no_secrets(self, mock_resource_filename):
        mock_resource_filename.return_value = 'tests/foo_no_secrets.yml'
        settings.init('loadtests.foo.locustfile', ['REQUIRED_KEY'])
        with open('tests/foo_no_secrets.yml') as foo:
            settings_documents = yaml.load_all(foo)
            foo_data = settings_documents.next()
            with self.assertRaises(StopIteration):
                settings_documents.next()
        assert settings.data == foo_data
        assert settings.secrets == {}
        self._reset_settings()
