"""
Performance tests for enrollment API.
"""
import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
import uuid
import random
from locust import HttpLocust, TaskSet, task

from helpers import settings
settings.init(__name__, required=[
    'COURSE_ID_LIST',
])

EMAIL_USERNAME = "success"
EMAIL_URL = "simulator.amazonses.com"
# Set a password for the users
USER_PASSWORD = "test"
ENROLLMENT_API_BASE_URL = "/api/enrollment/v1"


class NotAuthorizedException(Exception):
    """The API returned an HTTP status 403 """
    pass


class EnrollmentApi(object):
    """Interact with the enrollment API. """
    def __init__(self, hostname, client):
        """Initialize the client.

        Arguments:
            hostname (unicode): The hostname of the test server, sent as the "Referer" HTTP header.
            client (Session): The test client used by locust.

        """
        self.hostname = hostname
        self.client = client

        if settings.data.get('BASIC_AUTH_USER') is not None:
            self.client.auth = (
                settings.data['BASIC_AUTH_USER'],
                settings.data['BASIC_AUTH_PASS'],
            )

    def get_student_enrollments(self):
        """Retrieve enrollment info for the currently logged in user. """
        self._get("{0}/enrollment".format(ENROLLMENT_API_BASE_URL))

    def enroll(self, course_id):
        """Enroll the user in `course_id`. """
        url = u"{base}/enrollment".format(
            base=ENROLLMENT_API_BASE_URL
        )
        params = {'course_details': {'course_id': course_id}}
        self._post(url, json.dumps(params))

    def get_user_enrollment_status(self, user_name, course_id):
        """Check the user enrollment status in a given course. """
        url = u"{base}/enrollment/{user},{course_key}".format(
            base=ENROLLMENT_API_BASE_URL,
            user=user_name,
            course_key=course_id
        )
        name = u"{base}/enrollment/{{user}},{{course_key}}".format(base=ENROLLMENT_API_BASE_URL)
        self._get(url, name=name)

    def get_enrollment_detail_for_course(self, course_id):
        """Get enrollment details for a course. """
        url = u"{base}/course/{course_key}".format(
            base=ENROLLMENT_API_BASE_URL,
            course_key=course_id
        )
        name = u"{base}/course/{{course_key}}".format(base=ENROLLMENT_API_BASE_URL)
        self._get(url, name=name)

    @property
    def _post_headers(self):
        """Headers for a POST request, including the CSRF token. """
        return {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'X-CSRFToken': self.client.cookies.get('csrftoken', ''),
            'Referer': self.hostname
        }

    def _post(self, *args, **kwargs):
        """Make a POST request to the server.

        Skips SSL verification and sends the CSRF cookie.

        Raises a NotAuthorizedException if the server responds
        with a status 403.
        """
        kwargs['verify'] = False
        kwargs['headers'] = self._post_headers
        response = self.client.post(*args, **kwargs)
        self._check_response(response)
        return response

    def _get(self, *args, **kwargs):
        """Make a GET request to the server.

        Skips SSL verification.

        Raises a NotAuthorizedException if the server responds
        with a status 403.
        """
        kwargs['verify'] = False
        response = self.client.get(*args, **kwargs)
        self._check_response(response)
        return response

    def _check_response(self, response):
        """Check whether a response was successful. """
        if response.status_code == 403:
            raise NotAuthorizedException


class AutoAuthTaskSet(TaskSet):
    """Use the auto-auth end-point to create test users. """

    def auto_auth(self):
        """Create a new account with given credentials and log in.

        This requires that the test server has the feature flag
        `AUTOMATIC_AUTH_FOR_TESTING` set to True.

        """
        del self.client.cookies["sessionid"]
        self.username = "{0}{1}".format(EMAIL_USERNAME, uuid.uuid4().hex[:20])
        self.full_email = "{0}@{1}".format(self.username, EMAIL_URL)
        params = {
            'password': USER_PASSWORD,
            'email': self.full_email,
            'username': self.username,
        }
        self.client.get("/auto_auth", params=params, verify=False, name="/auto_auth")
        return self.username


class UserBehavior(TaskSet):
    """User scripts that exercise the enrollment API. """

    @task(5)
    class AuthenticatedAndEnrolledTasks(AutoAuthTaskSet):
        """User scripts in which the user is already authenticated and enrolled. """

        def on_start(self):
            """Ensure the user is logged in and enrolled. """
            self.api = EnrollmentApi(self.locust.host, self.client)
            self.auto_auth()

            # Ensure that the user is enrolled in all the courses
            for course_id in settings.data['COURSE_ID_LIST']:
                self.api.enroll(course_id)

        @task
        def user_enrollment_status(self):
            """Check a user's enrollment status in a course. """
            course_id = random.choice(settings.data['COURSE_ID_LIST'])

            try:
                self.api.get_user_enrollment_status(self.username, course_id)
            except NotAuthorizedException:
                self.auto_auth()

        @task
        def list_enrollments(self):
            """Get all enrollments for a user. """
            try:
                self.api.get_student_enrollments()
            except NotAuthorizedException:
                self.auto_auth()

    @task(5)
    class AuthenticatedButNotEnrolledTasks(AutoAuthTaskSet):
        """User scripts in which the user is authenticated but not enrolled. """

        def on_start(self):
            """Ensure the user is logged in """
            self.api = EnrollmentApi(self.locust.host, self.client)
            self.auto_auth()

        @task
        def user_enrollment_status(self):
            """Check a user's enrollment status in a course. """
            course_id = random.choice(settings.data['COURSE_ID_LIST'])
            try:
                self.api.get_user_enrollment_status(self.username, course_id)
            except NotAuthorizedException:
                self.auto_auth()

        @task
        def list_enrollments(self):
            """Get all enrollments for a user. """
            try:
                self.api.get_student_enrollments()
            except NotAuthorizedException:
                self.auto_auth()

    @task(5)
    class NotAuthenticatedTasks(TaskSet):
        """User scripts in which the user is not authenticated. """

        def on_start(self):
            self.api = EnrollmentApi(self.locust.host, self.client)

        @task
        def enrollment_detail_for_course(self):
            """Retrieve enrollment details for a course. """
            course_id = random.choice(settings.data['COURSE_ID_LIST'])
            self.api.get_enrollment_detail_for_course(course_id)

    @task(1)
    class EnrollNewUserTasks(AutoAuthTaskSet):
        """User scripts to enroll a user into a course for the first time. """

        def on_start(self):
            self.api = EnrollmentApi(self.locust.host, self.client)
            self._reset()

        @task
        def enroll(self):
            """First-time enrollment in a course. """
            # Since we can only enroll in a course once,
            # restart as a new user once we run out of courses.
            try:
                course_id = next(self.course_ids)
            except StopIteration:
                self._reset()
            else:
                try:
                    self.api.enroll(course_id)
                except NotAuthorizedException:
                    self._reset()

        def _reset(self):
            """Log in as a new user (with no enrollments). """
            self.auto_auth()
            self.course_ids = iter(settings.data['COURSE_ID_LIST'])


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1
    max_wait = 5
