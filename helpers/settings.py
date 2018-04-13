"""
This module helps manage settings files.  To use this module for your load
tests:

1. Include the following two lines in your locustfile.py:

     from helpers import settings
     settings.init(__name__)

2. Create a settings file: "settings_files/<TEST MODULE NAME>.yml"

   We assume the first YAML document contains non-secret settings, and the
   second document contains secrets.  The second YAML document is optional.

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
import copy
from pkg_resources import resource_filename
from pprint import pformat

LOG = logging.getLogger(__name__)
data = None
secrets = None


class MissingRequiredSettingError(Exception):
    pass


class MalformedSettingFileError(Exception):
    pass


class Settings(object):
    """
    Abstraction class for the standard edx-load-tests settings files syntax
    based on YAML.
    """

    def __init__(self, data=None, secrets=None):
        self._data = data or {}
        self._secrets = secrets or {}

    @property
    def data(self):
        return self._data

    @property
    def secrets(self):
        return self._secrets

    def __eq__(self, other):
        return self.data == other.data and self.secrets == other.secrets

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_file(cls, settings_file):
        """
        Factory method to create Settings instances from settings files.

        Arguments:
            settings_file (file):
                This open file object represents a settings file.

        Returns:
            A Settings instance containing the data and secrets from the given
            stream.
        """
        data, secrets = cls.load_file(settings_file)
        return cls(data, secrets)

    @classmethod
    def load_file(cls, settings_file):
        """
        Load the contents of the open file object as settings.

        Arguments:
            settings_file (file):
                This open file object represents a settings file.

        Returns:
            Two-tuple of dicts, where the first is settings data and the second
            is settings secrets.
        """
        settings_documents = list(yaml.safe_load_all(settings_file))

        # capture the data and secrets from their respective YAML documents
        data = None
        secrets = None
        if len(settings_documents) == 1:
            data, = settings_documents
        elif len(settings_documents) == 2:
            data, secrets = settings_documents
        elif len(settings_documents) > 2:
            raise MalformedSettingFileError("The settings file has more than two documents.")

        # YAML treats empty documents as None, we normalize it to an empty dict
        if data is None:
            data = {}
        if secrets is None:
            secrets = {}

        # Make sure we're actually returning dicts.  Documents in YAML could
        # contain things other than mappings, but that wouldn't be valid for
        # settings.
        # not_mappings is a list of error messages:
        not_mappings = [
            "{} has type '{}'".format(descriptor, type(obj).__name__)
            for descriptor, obj
            in {"first document": data, "second document": secrets}.items()
            if not isinstance(obj, dict)
        ]
        if not_mappings:
            # Say "mapping" in the error message instead of "dict" because
            # that's what they're called in YAML.
            raise MalformedSettingFileError(
                "One or more YAML documents in the settings file was not a mapping: {}.".format(', '.join(not_mappings))
            )

        return (data, secrets)

    def validate_required(self, required_data=(), required_secrets=()):
        """
        Validate the settings keys by making sure the required ones are
        present.

        Arguments:
            required_data (iterable of str):
                dict keys which we will be confirming are in self.data and not
                mapped to None.
            required_secrets (iterable of str):
                dict keys which we will be confirming are in self.secrets and
                not mapped to None.

        Raises:
            MissingRequiredSettingError: if there are any missing settings keys
        """
        missing_data_keys = [key for key in required_data if self.data.get(key) is None]
        missing_secret_keys = [key for key in required_secrets if self.secrets.get(key) is None]
        if missing_data_keys or missing_secret_keys:
            msgs = []
            import pdb
            pdb.set_trace()
            if missing_data_keys:
                msgs.append('Missing settings: {}.'.format(', '.join(missing_data_keys)))
            if missing_secret_keys:
                msgs.append('Missing secret settings: {}.'.format(', '.join(missing_secret_keys)))
            raise MissingRequiredSettingError(' '.join(msgs))

    def dump(self, stream):
        """
        Dump the generated settings file contents to the given stream.

        Arguments:
            stream (file):
                An open writable file object to dump settings into.
        """
        # only dump the secrets yaml document if it is populated
        docs_to_dump = [self.data]
        if self.secrets:
            docs_to_dump.append(self.secrets)

        yaml.safe_dump_all(
            docs_to_dump,
            stream=stream,
            default_flow_style=False,  # Represent objects using indented blocks
                                       # rather than inline enclosures.
            explicit_start=True,  # Begin the first document with '---', per
                                  # our usual settings file syntax.
        )

    def update(self, other_settings):
        """
        Merge other_settings into this one.

        Existing settings are overridden by those in other_settings, and the
        rest should remain unchanged.

        Arguments:
            other_settings (Settings):
                Another settings instance.
        """
        # Only work with a deep copy of other_settings, or else we might
        # transfer nested object references from other_settings into self,
        # causing self to contain a mix of shared and unshared values.
        other_settings_copy = copy.deepcopy(other_settings)
        self._data.update(other_settings_copy.data)
        self._secrets.update(other_settings_copy.secrets)


def init(test_module_full_name, required_data=(), required_secrets=()):
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
    try:
        with open(settings_filename, 'r') as settings_file:
            settings = Settings.from_file(settings_file)
    except MalformedSettingFileError as e:
        raise MalformedSettingFileError("{}: {}".format(settings_filename, e.message))

    # validation: make sure the required keys are present
    settings.validate_required(required_data, required_secrets)

    # produce output messages for future reference
    if settings.secrets:
        LOG.info('secrets loaded from the settings file')
    else:
        LOG.info('no secrets were specified in the settings file')
    LOG.info('loaded the following public settings:\n{}'.format(
        pformat(settings.data),
    ))

    # Copy loaded settings to globals.  The globals are used in load test code
    # to refer to settings, not the Settings object.
    data = settings.data
    secrets = settings.secrets
