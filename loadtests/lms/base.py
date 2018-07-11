"""
"""

import logging

from locust import TaskSet

from helpers.edx_app import EdxAppTasks
from helpers.mixins import EnrollmentTaskSetMixin
from helpers import settings


class LmsTasks(EnrollmentTaskSetMixin, EdxAppTasks):
    """
    Base class for course-specific LMS TaskSets.
    """

    @property
    def _is_child(self):
        """
        Returns True if the parent of this TaskSet instance is another TaskSet.
        """
        return isinstance(self.parent, TaskSet)

    def _request(self, method, path, *args, **kwargs):
        """
        Single internal helper for setting up course-specific LMS requests.
        """
        path = '/courses/{course_id}/' + path
        path = path.format(**{n: getattr(self, n) for n in ('course_id', 'course_num', 'course_run', 'course_org')})
        logging.debug(path)
        return getattr(self.client, method)(path, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Perform a GET, contextualizing the path for the course under test.

        String formatting placeholders for 'course_id', 'course_num', 'course_run', 'course_org'
        in the passed path will be evaluated and replaced.
        """
        return self._request('get', *args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Perform a POST, contextualizing the path for the course under test, and adding any
        mandatory request headers not explicitly passed in the call.

        String formatting placeholders for 'course_id', 'course_num', 'course_run', 'course_org'
        in the passed path will be evaluated and replaced.
        """
        headers = self.post_headers
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers
        return self._request('post', *args, **kwargs)

    def auto_auth(self, *args, **kwargs):
        success = super(LmsTasks, self).auto_auth(*args, **kwargs)
        if success and self._user_id and self._email and self._password:
            self.locust._user_id = self._user_id
            self.locust._email = self._email
            self.locust._password = self._password
        return success

    def login(self):
        success = False
        if self.locust._email and self.locust._password:
            response = self.client.post(
                settings.data['LOGIN_PATH'],
                data={'email': self.locust._email, 'password': self.locust._password},
                headers=self.post_headers,
                name='login'
            )
            success = response.status_code == 200

        if success:
            self.locust._is_logged_in = True
        return success

    def logout(self):
        response = self.client.get('/logout', name='logout', allow_redirects=False)

        success = response.ok
        if success:
            self.locust._is_logged_in = False
        return success

    def enroll(self, *args, **kwargs):
        success = super(LmsTasks, self).enroll(*args, **kwargs)
        if success:
            self.locust._is_enrolled = True
        return success

    def on_start(self):
        if not self.locust._is_registered:
            self.auto_auth(params={'no_login': True})

            # If we failed to register the user, and this TaskSet is a child of the main LmsTest TaskSet, interrupt so
            # that we can select another TaskSet and try to register again.
            #
            # NOTE: this is basically a retry mechanism without backoff, so it may behoove us to add delays to this
            if self._is_child and not self.locust._is_registered:
                self.interrupt()

        if self.locust._is_registered and not self.locust._is_logged_in:
            self.login()

            # If we failed to log in, and this TaskSet is a child of the main LmsTest TaskSet, interrupt so
            # that we can select another TaskSet and try to log in again.
            #
            # NOTE: this is basically a retry mechanism without backoff, so it may behoove us to add delays to this
            if self._is_child and not self.locust._is_logged_in:
                self.interrupt()

        if self.locust._is_logged_in and not self.locust._is_enrolled:
            self.enroll(self.course_id)

            # If we failed to enroll, and this TaskSet is a child of the main LmsTest TaskSet, interrupt so
            # that we can select another TaskSet and try to enroll again.
            #
            # NOTE: this is basically a retry mechanism without backoff, so it may behoove us to add delays to this
            if self._is_child and not self.locust._is_enrolled:
                self.interrupt()
