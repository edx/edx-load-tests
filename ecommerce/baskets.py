"""Locust tests related to basket operations."""
import json

from locust import task

from ecommerce.commerce import CommerceTasks
from ecommerce.config import FREE_COURSE_ID


class BasketsTasks(CommerceTasks):
    """Contains tasks which exercise basket-related behavior."""

    @task
    def purchase_single_free_product(self):
        """Simulate the purchase of a single free product via the LMS."""
        # If a user tries to purchase the same product more than once, we'll get 409s from
        # the LMS. To avoid this situation, we create a new user each time this task is called.
        self.auto_auth()

        post_data = {
            'course_id': FREE_COURSE_ID,
        }
        self.post('/api/commerce/v0/baskets/', data=json.dumps(post_data))
