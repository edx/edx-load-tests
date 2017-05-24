"""
Load test to access the cs_comments_service directly.

There are also tests that use the edx-platform comment client in locust/lms/forums.py

Usage:

  $ locust --host="http://localhost:18080"

Supported Environment Variables:

  CS_API_KEY - the shared secret between the LMS and the comments service. Must be set in order to run these tests.
  COURSE_ID - course id that we're running these tests against

"""

import os
import json
import random
import itertools

from locust import HttpLocust, task, TaskSet
from opaque_keys.edx.keys import CourseKey

API_PREFIX = '/api/v1'
USERS_FILE = 'comments_service_data/user_ids.json'
COMMENTABLES_FILE = 'comments_service_data/commentable_ids.json'
THREADS_FILE = 'comments_service_data/thread_ids.json'
COURSES_FILE = 'comments_service_data/course_ids.json'
USER_ID_INCREMENT_START = 10000000


class CommentsServiceTests(TaskSet):
    """
    Tests that directly access the comments service. Does not go through the LMS comment client.
    """
    # Use this increment value to generate new users.
    user_increment = itertools.count(
        int(os.getenv('USER_ID_INCREMENT_START', USER_ID_INCREMENT_START))
    ).next

    def __init__(self, *args, **kwargs):
        super(CommentsServiceTests, self).__init__(*args, **kwargs)
        self.api_key = os.getenv('CS_API_KEY')
        if self.api_key is None:
            raise Exception('No API key for the comments service was specified.')

        # Import scraped data from the comments service
        with open(os.getenv('USERS_FILE', USERS_FILE), 'r') as users_file:
            self.users = json.load(users_file)

        with open(os.getenv('THREADS_FILE', THREADS_FILE), 'r') as threads_file:
            self.threads = json.load(threads_file)

        with open(os.getenv('COMMENTABLES_FILE', COMMENTABLES_FILE), 'r') as commentables_file:
            self.commentables = json.load(commentables_file)

        with open(os.getenv('COURSES_FILE', COURSES_FILE), 'r') as courses_file:
            self.courses = json.load(courses_file)

    def _make_request(self, method, path, params=None, **kwargs):
        """
        Make a request from the comments service with the given method, path, and parameters.
        Arguments:
            method (str): HTTP method to execute.
            path (str): URL path to the resource being requested.
            params (dict) (optional): Dict of parameters to pass along in the request.
        """
        method = method.lower()
        headers = {
            'X-Edx-Api-Key': self.api_key,
            'content-type': 'application/json',
        }
        kwargs.update({'headers': headers})

        if params is not None:
            kwargs.update({'params': params})

        return getattr(self.client, method)(API_PREFIX + path, **kwargs)

    ###########################
    #  Generate or pick values
    ###########################

    def _pick_user(self):
        """ Pick a random user id from our list of known user ids. """
        return random.choice(self.users)

    def _pick_thread(self):
        """ Pick a thread from our list of known threads. """
        return random.choice(self.threads)

    def _pick_commentable(self):
        """ Pick a random commentable from our list of known commentables. """
        return random.choice(self.commentables)

    def _pick_course(self):
        """ Pick a random course from our list of known courses. """
        return random.choice(self.courses)

    def _generate_new_user(self):
        """ When we need to create new users, generate a new user_id, username, and e-mail. """
        user_id = unicode(self.user_increment())
        username = 'loadtest_user_{}'.format(user_id)
        email = 'loadtest_user_{}@example.com'.format(user_id)

        return user_id, username, email

    ###########################
    #   GET tests
    ###########################
    @task(50)
    def get_user(self):
        """ Access the user info endpoint. """
        user_id = self._pick_user()
        url_string = '/users/{}'
        self._make_request('GET', url_string.format(user_id), name=url_string.format('[user_id]'))

    @task(7)
    def get_threads(self):
        """ Get the threads for a course."""
        user_id = self._pick_user()
        course_id = self._pick_course()
        url_string = '/threads'
        self._make_request('GET', url_string, {
            'course_id': course_id,
            'recursive': 'false',
            'sort_key': 'date',
            'sort_order': 'desc',
            'per_page': '20',
            'user_id': user_id
        }, name=url_string)

    @task(28)
    def get_thread(self):
        """ Get a specific thread from the comments service. """
        thread_id = self._pick_thread()
        user_id = self._pick_user()
        url_string = '/threads/{}'
        self._make_request('GET', url_string.format(thread_id), {
            'user_id': user_id,
            'mark_as_read': 'true',
            'recursive': 'true',
        }, name=url_string.format('[thread_id]'))

    @task(4)
    def get_commentable_threads(self):
        """ Get all threads associated with a commentable_id. """
        commentable_id = self._pick_commentable()
        url_string = '/{}/threads'
        self._make_request('GET', url_string.format(commentable_id), {
            'recursive': 'false',
            'sort_order': 'desc',
            'per_page': '20',
            'page': '1'
        }, name=url_string.format('[commentable_id]'))

    @task
    def search_threads(self):
        """ Search the threads for a particular piece of text. """
        search_text = 'text'

        user_id = self._pick_user()
        course_id = self._pick_course()
        url_string = '/search/threads'
        self._make_request('GET', url_string, {
            'user_id': user_id,
            'recursive': 'false',
            'sort_key': 'votes',
            'text': search_text,
            'sort_order': 'desc',
            'course_id': course_id,
            'per_page': '20',
            'page': '1'
        }, name=url_string)

    @task
    def get_user_active_threads(self):
        """ Get the active threads for a user. """
        user_id = self._pick_user()
        course_id = self._pick_course()

        url_string = '/users/{}/active_threads'
        self._make_request('GET', url_string.format(user_id), {
            'course_id': course_id,
            'per_page': '20'
        }, name=url_string.format('[user_id]'))

    @task
    def get_user_subscribed_threads(self):
        """ Get the subscribed threads for a user. """
        user_id = self._pick_user()
        url_string = '/users/{}/subscribed_threads'
        self._make_request('GET', url_string.format(user_id), name=url_string.format('[user_id]'))

    ###########################
    #   POST tests
    ###########################
    @task
    def post_commentable_thread(self):
        """ Post a new thread to a commentable. """
        commentable_id = self._pick_commentable()
        user_id = self._pick_user()
        course_id = self._pick_course()

        url_string = '/{}/threads'
        self._make_request('POST', url_string.format(commentable_id), {
            'anonymous_to_peers': 'false',
            'user_id': user_id,
            'title': 'Hello World',
            'commentable_id': commentable_id,
            "thread_type": 'discussion',
            'anonymous': 'false',
            'course_id': course_id,
            'body': 'Hello World'
        }, name=url_string.format('[commentable_id]'))

    @task
    def post_threads_comment(self):
        """ Post a new comment on a thread. """

        user_id = self._pick_user()
        thread_id = self._pick_thread()
        course_id = self._pick_course()

        url_string = '/threads/{}/comments'
        self._make_request('POST', url_string.format(thread_id), {
            'body': 'Hello World',
            'anonymous_to_peers': 'false',
            'anonymous': 'false',
            'user_id': user_id,
            'course_id': course_id
        }, name=url_string.format('[thread_id]'))

    @task
    def post_subscriptions(self):
        """ Add a thread to subscriptions. """
        user_id = self._pick_user()
        thread_id = self._pick_thread()
        url_string = '/users/{}/subscriptions'
        self._make_request('POST', url_string.format(user_id), {
            'source_type': 'thread',
            'source_id': thread_id
        }, name=url_string.format('[user_id]'))

    ###########################
    #   PUT tests
    ###########################
    @task
    def put_votes_thread(self):
        """ Add a vote on a thread. """

        user_id = self._pick_user()
        thread_id = self._pick_thread()

        url_string = '/threads/{}/votes'
        self._make_request('PUT', url_string.format(thread_id), {
            'user_id': user_id,
            'value': 'up'
        }, name=url_string.format('[thread_id]'))

    @task(4)
    def put_user(self):
        """ Add a new user. """
        user_id, username, email = self._generate_new_user()

        url_string = '/users/{}'
        self._make_request('PUT', url_string.format(user_id), {
            'username': username,
            'email': email
        }, name=url_string.format('[user_id]'))


class CommentsServiceLocust(HttpLocust):
    task_set = CommentsServiceTests
    min_wait = int(os.getenv('LOCUST_MIN_WAIT', 500))
    max_wait = int(os.getenv('LOCUST_MAX_WAIT', 1000))
