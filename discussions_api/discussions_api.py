# pylint: disable=no-member
"""
Parent class of the discussion api tasks.
"""
import os

from helpers.auto_auth_tasks import AutoAuthTasks


class AutoAuthException(Exception):
    """The API returned an HTTP status 403 """
    pass


class DiscussionsApiTasks(AutoAuthTasks):
    """
    Parent class of the discussion api tasks.
    """

    def __init__(self, *args, **kwargs):  # pylint: disable=super-on-old-class
        super(DiscussionsApiTasks, self).__init__(*args, **kwargs)
        self.course_id = os.getenv('COURSE_ID')
        if os.getenv('SEEDED_DATA'):
            #with open("discussions_api/seed_data/" + os.getenv('SEEDED_DATA'), 'r') as seeded_data:
            with open("" + os.getenv('SEEDED_DATA'), 'r') as seeded_data:
                self.thread_id_list = seeded_data.read().splitlines()
        else:
            self.thread_id_list = []

        self.verbose = True if (os.getenv('VERBOSE') == "true") else False

    @property
    def _headers(self, content_type='application/json'):
        """Standard header"""
        return {
            'X-CSRFToken': self.client.cookies.get('csrftoken', ''),
            'Referer': self.locust.host,
            'content-type': 'application/merge-patch+json'
        }

    @property
    def _post_headers(self):
        """Headers for POST"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-CSRFToken': self.client.cookies.get('csrftoken', ''),
            'Referer': self.locust.host
        }

    @property
    def _delete_headers(self):
        """Headers for DELETE"""
        return {
            'X-CSRFToken': self.client.cookies.get('csrftoken', ''),
            'Referer': self.locust.host
        }

    def stop(self):
        """
        Supports usage as nested or top-level task set.
        """
        if self.parent != self.locust:
            self.interrupt()

    def on_start(self):
        if os.getenv('LOCUST_TASK_SET') != "DiscussionsApiTest":
            params = {
                "course_id": self.course_id,
                "staff": "true"
            }
            # "roles": ["Administrator"]
            self.auto_auth(verify_ssl=False, params=params)
