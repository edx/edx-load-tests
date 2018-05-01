from locust import task, TaskSet
from locust.clients import HttpSession

from helpers import settings
from helpers.api import LocustEdxRestApiClient
from loadtests.ecommerce_deadlock.ecommerce_deadlock_constants import SKU_LIST

ECOMMERCE_HOST = settings.data['ECOMMERCE_HOST'].rstrip('\/')


class EcommerceWorkerBasketTaskSet(TaskSet):
    """Task Set for the ecommerce worker."""

    def on_start(self):
        self.ecom_client = get_ecom_worker_client()

    @task(1)
    def get_basket_calculate(self):
        self.ecom_client.api.v2.baskets.calculate.get(sku=SKU_LIST)


def get_ecom_worker_client():
    """
    Gets the ecommerce worker client

    Using the oauth credentials in the settings file, this method
    returns up the ecommerce work clients which enables a task to call
    the api on behalf of the ecommerce worker.

    Returns:
        LocustEdxRestApiClient: The ecommerce worker client
    """
    access_token_endpoint = '{}/oauth2/access_token'.format(
        settings.secrets['oauth']['provider_url'].strip('/')
    )

    access_token, __ = LocustEdxRestApiClient.get_oauth_access_token(
        access_token_endpoint,
        settings.secrets['oauth']['client_id'],
        settings.secrets['oauth']['client_secret'],
    )

    return LocustEdxRestApiClient(
        ECOMMERCE_HOST,
        session=HttpSession(base_url=ECOMMERCE_HOST),
        oauth_access_token=access_token
    )
