"""Locust tests related to basket operations."""
import json

from locust import task

from commerce import CommerceTasks
from helpers import settings


class BasketsTasks(CommerceTasks):
    """Contains tasks which exercise basket-related behavior."""

    @task
    def get_basket_summary(self):
        """Simulate the get of a basket summary"""
        self.auto_auth()

        self.get('/basket')
