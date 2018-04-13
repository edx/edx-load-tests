import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

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


class SelfInterruptingTaskSet(TaskSet):
    @task(1)
    def stop(self):
        self.interrupt()


class BasketTaskSet(SelfInterruptingTaskSet):
    @task(20)
    def get_basket_summary(self):
        """Retrieve all courses associated with a catalog."""
        self.client.basket.get()

    @task(20)
    def get_basket_add(self):
        """http://localhost:18130/basket/add?sku=8CF08E5"""
        self.client.basket.add.get(sku='8CF08E5')

    @task(20)
    def get_basket_calculate(self):
        """http://localhost:18130/api/v2/baskets/calculate?sku=8CF08E5"""
        self.client.api.v2.baskets.calculate.get(sku='8CF08E5')


class EcommerceTaskSet(TaskSet):
    tasks = {
        BasketTaskSet: 1
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

        self.client = LocustEdxRestApiClient(
            api_url,
            session=HttpSession(base_url=self.host),
            oauth_access_token=access_token
        )
