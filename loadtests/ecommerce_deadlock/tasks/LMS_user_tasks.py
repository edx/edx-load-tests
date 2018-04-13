from locust import task, TaskSet

from helpers import settings
from loadtests.ecommerce_deadlock.ecommerce_deadlock_constants import SKU_LIST, USER_LOGIN_CREDENTIALS
from loadtests.ecommerce_deadlock.authentication import AuthenticationMixin

ECOMMERCE_HOST = settings.data['ECOMMERCE_HOST'].rstrip('\/')
LMS_HOST = settings.data['LMS_HOST'].rstrip('\/')


class BasketTaskSet(AuthenticationMixin, TaskSet):
    """
    Task Set rules for basket api calls.

    This TaskSet is meant to be used with an authentication method.
    """

    def on_start(self):
        """Raise an exception. This TaskSet is not meant to be run on its own."""
        raise Exception("This TaskSet is not meant to be run")

    @task(2)
    def get_basket_summary(self):
        """View the basket"""
        url = u"{base}/basket/".format(base=ECOMMERCE_HOST)
        self._get(url)

    @task(4)
    def get_basket_add(self):
        """
        Add products to basket

        This call will redirect to basket summary.
        """
        url = u"{base}/basket/add?{skus}".format(
            base=ECOMMERCE_HOST,
            skus=get_url_query_parameters_for_skus(SKU_LIST)
        )
        self._get(url)

    @task(8)
    def get_basket_calculate(self):
        """Calculate the basket price"""
        url = u"{base}/api/v2/baskets/calculate/?{skus}".format(
            base=ECOMMERCE_HOST,
            skus=get_url_query_parameters_for_skus(SKU_LIST)
        )
        self._get(url)

    def _get(self, *args, **kwargs):
        """Make a GET request to the server.

        Skips SSL verification.
        """
        kwargs['verify'] = False
        response = self.client.get(*args, **kwargs)
        return response


class AutoAuthUserBasketTaskSet(BasketTaskSet):
    """
    Task set for using auto auth users.

    This requires that the LMS host has the feature flag
    `AUTOMATIC_AUTH_FOR_TESTING` set to True.
    """
    def on_start(self):
        """Ensure the user is logged in and enrolled. """
        self.auto_auth_login()


class ManualUserBasketTaskSet(BasketTaskSet):
    """
    Task set for using manually created users.

    Set the USER_LOGIN_CREDENTIALS in the ecommerce_deadlock_constants.py file.

    Example:
        USER_LOGIN_CREDENTIALS = [
            ("clee+test1@edx.org", "edxedx11"),
            ("clee+test2@edx.org", "edxedx11"),
            ...
        ]
    """
    def on_start(self):
        email, password = USER_LOGIN_CREDENTIALS.pop()
        self.login(email, password)


def get_url_query_parameters_for_skus(skus):
    """
    Returns a string of skus formatted for a url

    Args:
        skus (list): A list of skus e.g. ["abcdef", "123456", "hellow"]

    Returns:
        string: "sku=abcdef&sku=123456&sku=hellow"

    """
    url_qp = ""
    for sku in skus:
        url_qp += "sku=" + sku + "&"
    if skus:
        url_qp = url_qp[:-1]
    return url_qp
