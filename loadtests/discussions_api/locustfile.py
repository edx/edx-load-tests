"""
Load tests for the Discussions API

These classes of tests are tests that run a suite of tasks that answers a single
question.

For example, DiscussionsApiTest is a test that only uses read operations and
is repeatable. Read operations are made significantly more than the
other operations so we use this as a baseline test.

GetThreadWithCommentsTest answers the question of how response times differ with
comment_counts.

FullDiscussionsApiTest is a ramping test with all the requests. This is meant to
simulate forums over time. Unfortunately, over time, the course will get slower
and slower because there will be more POSTs than DELETEs.

"""
import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import requests

from locust import HttpLocust

from discussions_api.dapi import DiscussionsApiTasks
from discussions_api.tasks.dapi_tasks import (
    DeleteCommentsTask,
    DeleteThreadsTask,
    GetThreadsTask,
    GetCommentsTask,
    GetThreadListTask,
    GetThreadWithCommentsTask,
    PatchCommentsTask,
    PatchThreadsTask,
    PostCommentsTask,
    PostThreadsTask,
)

requests.packages.urllib3.disable_warnings()

from helpers import settings
settings.init(__name__, required=[
    'COURSE_ID',
    'VERBOSE',
    'LOCUST_TASK_SET',
    'LOCUST_MIN_WAIT',
    'LOCUST_MAX_WAIT',
])


class DiscussionsApiTest(DiscussionsApiTasks):
    """
    This is a repeatable baseline test which utilizes the most used requests.

    PATCH, POST, and DELETE can affect the response times of the discussions
    API over time. Since the GET Thread and GET Thread List are used
    significantly more,  we use GET Thread and GET Thread List as the baseline
    since the requests are read only and the test is repeatable.
    """

    def on_start(self):
        """
        User is created here. When task is finished, user selects from tasks
        """
        params = {
            "course_id": self.course_id,
            "staff": "true",
            "roles": ["Administrator"]
        }
        self.auto_auth(verify_ssl=False, params=params)

    tasks = {
        GetThreadsTask: 5000,
        GetThreadListTask: 2500,
    }


class GetThreadWithCommentsTest(DiscussionsApiTasks):
    """
    This test will retrieve threads and report their comment_counts

    This test will retrieve threads, get it's comment_count and group itself
    in a range of comments in increments of 25 E.G. 0-25 comments, 26-50
    comments, 51-75 comments, etc... If pagination of comments is working
    correctly, the different comment_counts should have the same response time.
    """

    def on_start(self):
        """
        User is created here. When task is finished, user selects from tasks
        """
        params = {
            "course_id": self.course_id,
            "staff": "true",
            "roles": ["Administrator"]
        }
        self.auto_auth(verify_ssl=False, params=params)

    tasks = {
        GetThreadWithCommentsTask: 1
    }


class FullDiscussionsApiTest(DiscussionsApiTasks):
    """
    Runs all the available discussion API endpoints

    This test will use all the available discussion API endpoints. Over time
    test will change the response time of the course as it POSTs more threads
    than it DELETEs. As the course becomes larger, the response times become
    slower.

    Note: Currently GET_thread grabs its thread ids from a static list. POST
    does not add to this list. Over time, as more DELETE are done, more 404s
    will occur.
    """

    def on_start(self):
        """
        User is created here. When task is finished, user selects from tasks
        """
        params = {
            "course_id": self.course_id,
            "staff": "true",
            "roles": ["Administrator"],
        }
        self.auto_auth(verify_ssl=False, params=params)

    # TODO: Document updated numbers in wiki and update here following example in
    # - https://openedx.atlassian.net/wiki/display/MA/Goals+and+setup
    tasks = {
        GetThreadsTask: 7560,
        GetThreadListTask: 500,
        GetCommentsTask: 2000,
        PostThreadsTask: 220,
        PostCommentsTask: 500,
        PatchThreadsTask: 92,
        PatchCommentsTask: 83,
        DeleteThreadsTask: 40,
        DeleteCommentsTask: 300,
    }


class DiscussionsApiLocust(HttpLocust):
    task_set = globals()[settings.data['LOCUST_TASK_SET']]
    min_wait = settings.data['LOCUST_MIN_WAIT']
    max_wait = settings.data['LOCUST_MAX_WAIT']
