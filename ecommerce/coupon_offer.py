"""Locust tests related to coupon operations."""
from locust import task

from ecommerce.commerce import CommerceTasks
from ecommerce.config import COUPON_CODE, ECOMMERCE_SERVICE_URL, PAID_SKU


class CouponOfferTasks(CommerceTasks):
    """Contains tasks which exercise coupon-related behavior."""

    @task
    def visit_offer_page(self):
        """Simulate anonymous user loading the coupon offer landing page."""
        offer_url = '{}/coupons/offer/?code={}'.format(ECOMMERCE_SERVICE_URL, COUPON_CODE)
        self.client.get(offer_url)

    @task
    def redeem_coupon(self):
        """Simulate a user redeeming a coupon."""
        self.auto_auth()
        redeem_url = '{}/coupons/redeem/?code={}&sku={}'.format(ECOMMERCE_SERVICE_URL, COUPON_CODE, PAID_SKU)
        self.client.get(redeem_url)
