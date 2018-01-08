"""
Load test for the Course Completion API performance
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from locust import HttpLocust, TaskSet, task, events
from locust.clients import HttpSession

from helpers import settings, markers
from helpers.api import LocustEdxRestApiClient


# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import requests.exceptions
import json
import random
import string
from locust import HttpLocust, task
from helpers.auto_auth_tasks import AutoAuthTasks
from helpers import settings, markers

settings.init(__name__, required_data=[
    'html',
    'video',
    'COURSE_ID',
    'LOCUST_MIN_WAIT',
    'LOCUST_MAX_WAIT',
])

markers.install_event_markers()

_dummy_chars = string.lowercase + ' '


class CompletionAPITaskSet(AutoAuthTasks):
    """
    Tests the course completion API.
    """

    def __init__(self, *args, **kwargs):
        super(CompletionAPITaskSet, self).__init__(*args, **kwargs)

        self.course_id = settings.data['COURSE_ID']
        self.chapter_id = settings.data['chapter_id']
        self.html_ids = {
            'section': settings.data['html']['section_id'],
            'vertical': settings.data['html']['vertical_id'],
            'xblock': settings.data['html']['xblock_id']
        }
        self.video_ids = {
            'section': settings.data['video']['section_id'],
            'vertical': settings.data['video']['vertical_id'],
            'xblock': settings.data['video']['xblock_id']
        }

    @property
    def _headers(self):
        return {
            'X-CSRFToken': self.client.cookies.get('csrftoken', ''),
            'Referer': self.locust.host,
        }

    def on_start(self):
        """ Auth user and enroll the student. """
        self.auto_auth()
        self.enroll()

    def enroll(self):
        """
        Enroll the student in the given course.
        """
        self.client.post(
            '/change_enrollment',
            data={'course_id': self.course_id, 'enrollment_action': 'enroll'},
            headers=self._headers,
            name='enroll',
        )

    def _get_xblock_and_publish_completion(self, block_ids):
        """
        View a section and mark that section completed in the completion API.
        """

        self.client.get(
            '/courses/{}/courseware/{}/{}'.format(
                self.course_id,
                self.chapter_id,
                block_ids['section']
            ),
            headers=self._headers,
        )

        return self.client.post(
            '/courses/{}/xblock/{}/handler/publish_completion'.format(
                self.course_id,
                block_ids['vertical']
            ),
            data=json.dumps({"block_key": block_ids['xblock'], "completion": 1.0}),
            headers=self._headers,
        )

    @task
    def view_html_block(self):
        """
        View an html xblock and mark it as completed.
        """
        self._get_xblock_and_publish_completion(self.html_ids)

    @task
    def view_video(self):
        """
        View a video and mark it as completed.
        """
        self._get_xblock_and_publish_completion(self.video_ids)


class CompletionApiLocust(HttpLocust):
    task_set = CompletionAPITaskSet
    min_wait = settings.data['LOCUST_MIN_WAIT']
    max_wait = settings.data['LOCUST_MAX_WAIT']
