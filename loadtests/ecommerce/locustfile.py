import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import uuid
import random

from locust import HttpLocust, task, TaskSet
from locust.clients import HttpSession

from helpers import settings, markers
from helpers.api import LocustEdxRestApiClient

settings.init(
    __name__,
    required_secrets=['oauth'],
)

markers.install_event_markers()

EMAIL_USERNAME = "success"
EMAIL_URL = "simulator.amazonses.com"
# Set a password for the users
USER_PASSWORD = "test"

SKUS = ["A967F95", "E0155EE", "CBA1948", "CBA1948", "8AE70EF", "A967F95"]
HOST = "http://localhost:18130"


class AutoAuthTaskSet(TaskSet):
    """Use the auto-auth end-point to create test users. """

    def auto_auth(self):
        """Create a new account with given credentials and log in.

        This requires that the test server has the feature flag
        `AUTOMATIC_AUTH_FOR_TESTING` set to True.

        """
        del self.client.cookies["sessionid"]
        self.username = "{0}{1}".format(EMAIL_USERNAME, uuid.uuid4().hex[:20])
        self.full_email = "{0}@{1}".format(self.username, EMAIL_URL)
        params = {
            'password': USER_PASSWORD,
            'email': self.full_email,
            'username': self.username,
        }
        self.client.get("/auto_auth", params=params, verify=False, name="/auto_auth")
        return self.username


class SelfInterruptingTaskSet(TaskSet):
    @task(1)
    def stop(self):
        self.interrupt()


class BasketTaskSet(SelfInterruptingTaskSet):
    @task(20)
    def get_basket_summary(self):
        """Retrieve all courses associated with a catalog."""
        self.ecom_client.basket.get()

    @task(20)
    def get_basket_add(self):
        """http://localhost:18130/basket/add?sku=8CF08E5"""
        self.ecom_client.basket.add.get(sku=SKUS)

    @task(20)
    def get_basket_calculate(self):
        """http://localhost:18130/api/v2/baskets/calculate?sku=8CF08E5"""
        self.ecom_client.api.v2.baskets.calculate.get(sku=SKUS)


class AuthBasketTaskSet(AutoAuthTaskSet):

    def on_start(self):
        """Ensure the user is logged in and enrolled. """
        self.auto_auth()

    @task(20)
    def get_basket_summary(self):
        """Retrieve all courses associated with a catalog."""
        url = u"{base}/basket".format(base=HOST)
        self._get(url)

    @task(20)
    def get_basket_add(self):
        """http://localhost:18130/basket/add?sku=8CF08E5"""
        url = u"{base}/basket/add?{skus}".format(
            base=HOST,
            skus=self._get_skus()
        )
        self._get(url)

    @task(20)
    def get_basket_calculate(self):
        """http://localhost:18130/api/v2/baskets/calculate?sku=8CF08E5"""
        url = u"{base}/api/v2/baskets/calculate?{skus}".format(
            base=HOST,
            skus=self._get_skus()
        )
        self._get(url)

    def _get_skus(self):
        skus = ""
        for sku in SKUS:
            skus += "sku=" + sku + "&"
        return skus

    def _get(self, *args, **kwargs):
        """Make a GET request to the server.

        Skips SSL verification.

        Raises a NotAuthorizedException if the server responds
        with a status 403.
        """
        kwargs['verify'] = False
        response = self.client.get(*args, **kwargs)
        self._check_response(response)
        return response

    def _check_response(self, response):
        """Check whether a response was successful. """
        if response.status_code == 403:
            raise Exception


class EcommerceTaskSet(TaskSet):
    tasks = {
        AuthBasketTaskSet: 1,
        # BasketTaskSet: 1
    }


class EcommerceLocust(HttpLocust):
    """Representation of a user.

    Locusts are hatched and used to attack the system being load tested. This class
    defines which TaskSet class should control each locust's behavior.
    """
    min_wait = 3 * 1000
    max_wait = 5 * 1000
    task_set = EcommerceTaskSet

    def __init__(self):
        super(EcommerceLocust, self).__init__()

        access_token_endpoint = '{}/oauth2/access_token'.format(
            settings.secrets['oauth']['provider_url'].strip('/')
        )

        access_token, __ = LocustEdxRestApiClient.get_oauth_access_token(
            access_token_endpoint,
            settings.secrets['oauth']['client_id'],
            settings.secrets['oauth']['client_secret'],
        )

        api_url = self.host.strip('/')

        self.ecom_client = LocustEdxRestApiClient(
            api_url,
            session=HttpSession(base_url=self.host),
            oauth_access_token=access_token
        )
