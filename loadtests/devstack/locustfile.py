"""
Load tests for devstack.

These tests can be used to assess the performance of devstack--Docker or Vagrant.
Currently they only exercise the LMS. In the future, we may update them to test
other services; however, no plans have been made to do so.
"""
import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from locust import HttpLocust, task, TaskSet

from helpers import settings, markers
from helpers.auto_auth_tasks import AutoAuthTasks
from helpers.mixins import EnrollmentTaskSetMixin

settings.init(__name__, required_data=[
    'course',
    'LOCUST_MIN_WAIT',
    'LOCUST_MAX_WAIT',
])

markers.install_event_markers()


class LMSDevstackTasks(EnrollmentTaskSetMixin, AutoAuthTasks):
    @property
    def course_id(self):
        return settings.data['course']

    def on_start(self):
        self.auto_auth()
        self.enroll(self.course_id)

    @task()
    def get_learner_dashboard(self):
        self.client.get('/dashboard')

    @task(0)
    def get_account_settings(self):
        self.client.get('/account/settings')

    @task()
    def get_learner_profile(self):
        self.client.get('/u/{}'.format(self._username), name='learner_profile')

    @task()
    def get_course_about_page(self):
        self.client.get('/courses/{}/about'.format(self.course_id))

    @task()
    def get_course_listing(self):
        self.client.get('/courses')


class DevstackTaskSet(TaskSet):
    tasks = {
        LMSDevstackTasks: 1,
    }


class DevstackLocust(HttpLocust):
    task_set = DevstackTaskSet
    min_wait = settings.data['LOCUST_MIN_WAIT']
    max_wait = settings.data['LOCUST_MAX_WAIT']
