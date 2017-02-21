import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from collections import deque
import random

from locust import task, HttpLocust
from locust.clients import HttpSession

from helpers import settings
from helpers.api import LocustEdxRestApiClient
from helpers.auto_auth_tasks import AutoAuthTasks

settings.init(__name__, required_data=['credentials'], required_secrets=['oauth'])

CREDENTIAL_SERVICE_URL = settings.data['credentials']['url']['service']
LMS_ROOT_URL = settings.data['credentials']['lms_url_root']
PROGRAM_UUID = settings.data['credentials']['program_uuid']
USERNAME = settings.data['credentials']['username']


class CredentialTaskSet(AutoAuthTasks):
    """Tasks exercising Credential functionality."""

    # Keep track of credential UUIDs created during a test, so they can be used to formulate read requests, and patch
    # requests. A deque is used instead of a list in order to enforce maximum length.
    _user_credentials = deque(maxlen=1000)

    def on_start(self):
        self.user_credential_client = self.get_credential_client()

    def get_credential_client(self):
        """ New property added for using LocustEdxRestApiClient.
        Default locust client will remain same for using auto_auth().
        """
        return LocustEdxRestApiClient(
            settings.data['credentials']['url']['api'],
            session=HttpSession(base_url=self.locust.host),
            jwt=self.get_access_token()
        )

    @staticmethod
    def get_access_token():
        """ Returns the OAuth 2.0 access token for the Credentials Service.

        Returns:
            str: JWT
        """
        access_token_url = settings.secrets['oauth']['access_token_url']
        client_id = settings.secrets['oauth']['client_id']
        client_secret = settings.secrets['oauth']['client_secret']
        access_token, __ = LocustEdxRestApiClient.get_oauth_access_token(access_token_url, client_id, client_secret,
                                                                         token_type='jwt')
        return access_token

    @task(1000)
    def list_user_credential_with_username(self):
        """ Get all credentials for a user."""
        self.user_credential_client.credentials.get(username=USERNAME)

    @task
    def list_user_credential_with_username_and_status(self):
        """ Get credentials having awarded status for a user."""
        self.user_credential_client.credentials.get(username=USERNAME, status='awarded')

    @task
    def list_credentials_filtered_by_program_uuid(self):
        """ Get credentials filtered by program UUID."""
        self.user_credential_client.credentials.get(program_uuid=PROGRAM_UUID)

    @task
    def list_credentials_filtered_by_program_uuid_and_status(self):
        """ Get credentials filtered by program UUID and status."""
        self.user_credential_client.credentials.get(program_uuid=PROGRAM_UUID, status='awarded')

    @task
    def post_credential_with_attribute(self):
        # We are creating new user on LMS for generating its credentials,
        # user information will be used in rendering of credentials.
        self.auto_auth(hostname=LMS_ROOT_URL)
        data = {
            'username': self._username,
            'credential': {'program_uuid': PROGRAM_UUID},
            'attributes': [{'name': 'whitelist_reason', 'value': 'Load testing'}]
        }
        user_credential = self.user_credential_client.credentials.post(
            data=data,
            name='/api/v2/credentials/(with_attributes)'
        )
        self._user_credentials.append(user_credential['uuid'])

    @task
    def post_credential_without_attribute(self):
        # We are creating new user on LMS for generating its credentials,
        # user information will be used in rendering of credentials.
        self.auto_auth(hostname=LMS_ROOT_URL)
        data = {
            'username': self._username,
            'credential': {'program_uuid': PROGRAM_UUID},
            'attributes': []
        }
        user_credential = self.user_credential_client.credentials.post(
            data=data,
            name='/api/v2/credentials/(without_attributes)'
        )
        self._user_credentials.append(user_credential['uuid'])

    @task
    def get_credential(self):
        if not self._user_credentials:
            return

        credential_uuid = random.choice(self._user_credentials)
        self.user_credential_client.credentials(credential_uuid).get(name='/api/v2/credentials/[uuid]')

    @task
    def patch_credential(self):
        """ Randomly picked the status for patching the credentials. In case of revoke status remove the
        record from the deque. Otherwise during rendering task it will return 404.
        """
        if not self._user_credentials:
            return

        credential_uuid = random.choice(self._user_credentials)
        status = random.choice(['awarded', 'revoked'])
        data = {'status': status}
        if status == 'revoked':
            self._user_credentials.remove(credential_uuid)
        self.user_credential_client.credentials(credential_uuid).patch(data=data, name='/api/v2/credentials/[uuid]')

    @task(10)
    def render_credential(self):
        """ Render a credential. """
        if not self._user_credentials:
            return

        credential_uuid = random.choice(self._user_credentials)
        url = '{}/credentials/{}/'.format(CREDENTIAL_SERVICE_URL.strip('/'), credential_uuid)
        self.client.get(url, name='/credentials/[uuid]')


class CredentialsLocust(HttpLocust):
    """Representation of an HTTP "user" to be hatched.

    Hatched users will be used to attack the system being load tested. This class
    defines which TaskSet class should define the user's behavior and how long a simulated
    user should wait between executing tasks. This class also provides a custom client used
    to interface with edX REST APIs.
    """

    min_wait = 30
    max_wait = 100
    task_set = CredentialTaskSet
