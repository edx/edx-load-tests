import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import datetime
import uuid

import jwt
from locust import TaskSet, task, HttpLocust
from locust.clients import HttpSession
from locust.exception import LocustError

from helpers.api import LocustEdxRestApiClient
from programs.config import PROGRAMS_API_URL, JWT_AUDIENCE, JWT_ISSUER, JWT_EXPIRATION_DELTA, JWT_SECRET_KEY


class ProgramsTaskSet(TaskSet):
    """Tasks exercising Programs functionality."""
    @task
    def list_programs(self):
        self.client.programs.get()


class ProgramsUser(HttpLocust):
    """Representation of an HTTP "user" to be hatched.

    Hatched users will be used to attack the system being load tested. This class
    defines which TaskSet class should define the user's behavior and how long a simulated
    user should wait between executing tasks. This class also provides a custom client used
    to interface with edX REST APIs.
    """
    # Django's AbstractUser, subclassed by Programs, limits usernames to 30 characters.
    # See: https://github.com/django/django/blob/stable/1.8.x/django/contrib/auth/models.py#L385
    USERNAME_MAX_LENGTH = 30
    USERNAME_PREFIX = 'load-test-'

    task_set = ProgramsTaskSet
    min_wait = 30
    max_wait = 100

    def __init__(self):
        super(ProgramsUser, self).__init__()

        if not self.host:
            raise LocustError(
                'You must specify a base host, either in the host attribute in the Locust class, '
                'or on the command line using the --host option.'
            )

        self.client = LocustEdxRestApiClient(
            PROGRAMS_API_URL,
            session=HttpSession(base_url=self.host),
            jwt=self._get_token()
        )

    def _get_token(self):
        # Keep the length of the resulting username within Django's prescribed limits.
        username_suffix = uuid.uuid4().hex[:self.USERNAME_MAX_LENGTH - len(self.USERNAME_PREFIX)]

        payload = {
            'preferred_username': self.USERNAME_PREFIX + username_suffix,
            'iss': JWT_ISSUER,
            'aud': JWT_AUDIENCE,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=JWT_EXPIRATION_DELTA),
        }

        return jwt.encode(payload, JWT_SECRET_KEY)
