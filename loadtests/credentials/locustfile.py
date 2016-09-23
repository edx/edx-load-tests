import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from collections import deque
import datetime
import random
import uuid

import jwt
from locust import task, HttpLocust
from locust.clients import HttpSession
from locust.exception import LocustError

from helpers.api import LocustEdxRestApiClient
from helpers.auto_auth_tasks import AutoAuthTasks

# FIXME: This load test does not yet implement the settings interface in
# helpers/settings.py.
from config import CREDENTIAL_API_URL, CREDENTIAL_SERVICE_URL, JWT, LMS_ROOT_URL, PROGRAM_ID, USERNAME


class CredentialTaskSet(AutoAuthTasks):
    """Tasks exercising Credential functionality."""

    # Keep track of credential ids created during a test, so they can be used to formulate read requests, and patch
    # requests. A deque is used instead of a list in order to enforce maximum length.
    _user_credentials = deque(maxlen=1000)

    def on_start(self):
        self.user_credential_client = self.get_credential_client()

    def get_credential_client(self):
        """ New property added for using LocustEdxRestApiClient.
        Default locust client will remain same for using auto_auth().
        """
        return LocustEdxRestApiClient(
            CREDENTIAL_API_URL,
            session=HttpSession(base_url=self.locust.host),
            jwt=self._get_token()
        )

    def _get_token(self):
        username_prefix = "load-test-"

        # Django's AbstractUser, subclassed by Credentials, limits usernames to 30 characters.
        # Keep the length of the resulting username within Django's prescribed limits.
        username_suffix = uuid.uuid4().hex[:30 - len(username_prefix)]
        payload = {
            'preferred_username': username_prefix + username_suffix,
            'iss': JWT["JWT_ISSUER"],
            'aud': JWT["JWT_AUDIENCE"],
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=JWT["JWT_EXPIRATION_DELTA"]),
            'administrator': True
        }
        return jwt.encode(payload, JWT["JWT_SECRET_KEY"])

    @task(1000)
    def list_user_credential_with_username(self):
        """ Get all credentials for a user."""
        self.user_credential_client.user_credentials.get(username=USERNAME)

    @task
    def list_user_credential_with_username_and_status(self):
        """ Get credentials having awarded status for a user."""
        self.user_credential_client.user_credentials.get(username=USERNAME, status="awarded")

    @task
    def list_program_credential_with_programs_id(self):
        """ Get credentials of any any status for a program id."""
        self.user_credential_client.program_credentials.get(program_id=PROGRAM_ID)

    @task
    def list_program_credential_with_program_id_and_status(self):
        """ Get credentials having awarded status for a program id."""
        self.user_credential_client.program_credentials.get(program_id=PROGRAM_ID, status="awarded")

    @task
    def post_credential_with_attribute(self):
        # We are creating new user on LMS for generating its credentials,
        # user information will be used in rendering of credentials.
        self.auto_auth(hostname=LMS_ROOT_URL)
        data = {
            "username": self._username,
            "credential": {"program_id": PROGRAM_ID},
            "attributes": [{"name": "whitelist_reason", "value": "Reason for whitelisting."}]
        }
        user_credential = self.user_credential_client.user_credentials.post(
            data=data,
            name="/api/v1/user_credentials/(with_attributes)"
        )
        self._user_credentials.append((user_credential["id"], user_credential["uuid"]))

    @task
    def post_credential_without_attribute(self):
        # We are creating new user on LMS for generating its credentials,
        # user information will be used in rendering of credentials.
        self.auto_auth(hostname=LMS_ROOT_URL)
        data = {
            "username": self._username,
            "credential": {"program_id": PROGRAM_ID},
            "attributes": []
        }
        user_credential = self.user_credential_client.user_credentials.post(
            data=data,
            name="/api/v1/user_credentials/(without_attributes)"
        )
        self._user_credentials.append((user_credential["id"], user_credential["uuid"]))

    @task
    def get_credential(self):
        if not self._user_credentials:
            return

        credential_id = random.choice(self._user_credentials)[0]
        self.user_credential_client.user_credentials(credential_id).get(name="/api/v1/user_credentials/[id]")

    @task
    def patch_credential(self):
        """ Randomly picked the status for patching the credentials. In case of revoke status remove the
        record from the deque. Otherwise during rendering task it will return 404.
        """
        if not self._user_credentials:
            return

        user_credentials = random.choice(self._user_credentials)
        status = random.choice(["awarded", "revoked"])
        data = {"status": status}
        if status == "revoked":
            self._user_credentials.remove(user_credentials)
        self.user_credential_client.user_credentials(user_credentials[0]).patch(
            data=data, name="/api/v1/user_credentials/[id]"
        )

    @task(10)
    def render_credential(self):
        """ Render a user credential. """
        if not self._user_credentials:
            return

        credential_uuid = random.choice(self._user_credentials)[1]
        self.client.get("{}/credentials/{}/".format(CREDENTIAL_SERVICE_URL, credential_uuid.replace("-", "")),
                        name="/credentials/[uuid]")


class CredentialUser(HttpLocust):
    """Representation of an HTTP "user" to be hatched.

    Hatched users will be used to attack the system being load tested. This class
    defines which TaskSet class should define the user's behavior and how long a simulated
    user should wait between executing tasks. This class also provides a custom client used
    to interface with edX REST APIs.
    """

    task_set = CredentialTaskSet
    min_wait = 30
    max_wait = 100

    def __init__(self):
        super(CredentialUser, self).__init__()

        if not self.host:
            raise LocustError(
                'You must specify a base host, either in the host attribute in the Locust class, '
                'or on the command line using the --host option.'
            )
