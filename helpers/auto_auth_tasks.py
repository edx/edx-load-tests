import json
from locust import TaskSet

from helpers import settings


class AutoAuthTasks(TaskSet):
    """
    Methods useful to any/all tests that want to use auto auth.
    """

    def __init__(self, *args, **kwargs):
        """
        Add basic auth credentials to our client object when specified.
        """
        super(AutoAuthTasks, self).__init__(*args, **kwargs)

        if settings.secrets.get('BASIC_AUTH_USER') is not None:
            self.client.auth = (
                settings.secrets['BASIC_AUTH_USER'],
                settings.secrets['BASIC_AUTH_PASS'],
            )

        self._user_id = None
        self._anonymous_user_id = None
        self._username = None
        self._email = None
        self._password = None

    def auto_auth(self, verify_ssl=True, params=None, hostname=''):
        """
        Logs in with a new, programmatically-generated user account.
        Requires AUTO_AUTH functionality to be enabled in the target edx instance.
        """
        if 'sessionid' in self.client.cookies:
            del self.client.cookies['sessionid']

        response = self.client.get(
            '{}/auto_auth'.format(hostname),
            name="auto_auth",
            headers={'Accept': 'application/json'},
            params=params or {},
            verify=verify_ssl
        )

        if response.status_code == 200:
            try:
                json_response = response.json()
                self._username = json_response['username']
                self._email = json_response['email']
                self._password = json_response['password']
                self._user_id = json_response['user_id']
                self._anonymous_user_id = json_response['anonymous_id']
                return True
            except ValueError, KeyError:
                pass

        return False
