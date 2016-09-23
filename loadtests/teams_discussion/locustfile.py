"""
Load test to test the performance of teams discussions.
"""
import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from collections import deque
import json
import random
import string

from locust import HttpLocust, task

from helpers.auto_auth_tasks import AutoAuthTasks

from helpers import settings
settings.init(__name__, required=[
    'COURSE_ID',
    'LOCUST_MIN_WAIT',
    'LOCUST_MAX_WAIT',
])


_dummy_chars = string.lowercase + ' '


def _dummy_text(minlen, maxlen):
    """
    Generate dummy text for forum submissions.
    """
    return "".join(random.choice(_dummy_chars) for _ in xrange(minlen, random.randrange(minlen + 1, maxlen)))


class TeamsDiscussionTasks(AutoAuthTasks):
    """
    Tests that post to team discussions.
    """
    _teams = []

    def __init__(self, *args, **kwargs):
        super(TeamsDiscussionTasks, self).__init__(*args, **kwargs)

        self.course_id = settings.data['COURSE_ID']
        self._thread_ids = deque(maxlen=100)

    def on_start(self):
        """ Auth user and enroll the student. """
        self.auto_auth()
        self.enroll()
        if not self._teams:
            self._teams = self.get_teams()
        self.join_team()

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

    def get_teams(self):
        """
        Get teams information about the course's teams via the API.
        """
        url = "/api/team/v0/teams/"
        response_json = self._make_request(
            'get',
            url,
            params={'course_id': self.course_id},
            name='get teams'
        ).json()

        num_pages = min(int(response_json['num_pages']), 20)
        teams = response_json['results']

        for page in xrange(2, num_pages):
            response_json = self._make_request(
                'get',
                url,
                params={'course_id': self.course_id, 'page': page},
                name='get teams'
            ).json()
            teams = teams + response_json['results']

        return teams

    def _pick_team(self):
        """ Pick a random team from our list of teams. """
        return random.choice(self._teams)

    def join_team(self):
        """
        Get the current user to join a team.
        """
        # Pick the team this user will be on.
        self.team = self._pick_team()
        url = '/api/team/v0/team_membership/'

        self._make_request(
            'post',
            url,
            data={'team_id': self.team['id'], 'username': self._username},
            name='join_team'
        )

    @property
    def _headers(self):
        return {
            'X-CSRFToken': self.client.cookies.get('csrftoken', ''),
            'Referer': self.locust.host,
        }

    def _make_request(self, method, path, params=None, **kwargs):
        """
        Make a request to the teams API with the given method, path, and parameters.
        Arguments:
            method (str): HTTP method to execute.
            path (str): URL path to the resource being requested.
            params (dict) (optional): Dict of parameters to pass along in the request.
        """
        method = method.lower()
        kwargs.update({'headers': self._headers})

        if params is not None:
            kwargs.update({'params': params})

        return getattr(self.client, method)(path, **kwargs)

    @task(2)
    def view_team_page(self):
        """ View the page for the users' current team. """
        url = "/courses/{course_id}/teams/#teams/{topic_id}/{team_id}"
        self._make_request(
            'get',
            url.format(course_id=self.course_id, topic_id=self.team['topic_id'], team_id=self.team['id']),
            name=url.format(course_id="[course_id]", topic_id="[topic_id]", team_id="[team_id]")
        )

    @task
    def create_thread(self):
        """ Create a thread in the team's discussion. """
        thread_data = {
            'body': _dummy_text(100, 2000),  # NB size range not based on actual data.
            'title': _dummy_text(20, 100),  # NB size range not based on actual data.
            'thread_type': random.choice(('discussion', 'question')),
            'anonymous_to_peers': 'false',
            'anonymous': 'false',
            'auto_subscribe': 'true',
        }
        discussion_id = self.team['discussion_topic_id']

        url = '/courses/{course_id}/discussion/{discussion_id}/threads/create'
        response = self._make_request(
            'post',
            url.format(course_id=self.course_id, discussion_id=discussion_id),
            data=thread_data,
            name=url.format(course_id="[course_id]", discussion_id="[discussion_topic_id]"),
        )

        # Add the thread to our local list.
        self._thread_ids.append((discussion_id, response.json()['id']))

    @task
    def add_comment(self):
        """ Add a comment to an existing thread """
        if not self._thread_ids:
            # Don't want to add a comment if we don't have any threads.
            return

        _, thread_id = random.choice(self._thread_ids)

        thread_data = {
            'body': _dummy_text(100, 2000)
        }

        url = '/courses/{course_id}/discussion/threads/{thread_id}/reply'
        self._make_request(
            'post',
            url.format(course_id=self.course_id, thread_id=thread_id),
            data=thread_data,
            name=url.format(course_id="[course_id]", thread_id="[thread_id]")
        )


class TeamsDiscussionLocust(HttpLocust):
    task_set = TeamsDiscussionTasks
    min_wait = settings.data['LOCUST_MIN_WAIT']
    max_wait = settings.data['LOCUST_MAX_WAIT']
