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


Usage:

  $ locust --host="http://localhost:8000"

Supported Environment Variables:

  BASIC_AUTH_USER, BASIC_AUTH_PASS - if set, will use for HTTP Authentication
  LOCUST_TASK_SET - if set, will run the specified TaskSet (must be imported in this module)
  COURSE_ID - course that will be tested on the target host, default is set in lms.LmsTasks
  SEEDED_DATA - required for the any test that uses GET Thread
  LOCUST_MIN_WAIT - Minimum wait time
  LOCUST_MAX_WAIT = Maximum wait time

"""
import os
import requests

from locust import HttpLocust

from dapi import DiscussionsApiTasks
from tasks.dapi_tasks import (
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
            "staff": "true"
        }
        #"roles": ["Administrator"]
        self.auto_auth(verify_ssl=False, params=params)

    tasks = {
        GetThreadsTask: 5000,
        GetThreadListTask: 2500,
        GetCommentsTask: 2000,
    }

    #tasks = {
        # DeleteCommentsTask: 40,
        # DeleteThreadsTask: 40,
        # GetCommentsTask: 2000,
        # GetThreadsTask: 7560,
        # PatchCommentsTask: 83,
        #PatchThreadsTask: 92,
        #PostCommentsTask: 194,
        #PostThreadsTask: 220,
    #}
    
    
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
        #GetThreadWithCommentsTask: 1
    }


class FullDiscussionsApiTest(DiscussionsApiTasks):
    """
    Runs all the available discussion API endpoints

    This test will use all the available discussion API endpoints. Over time
    test will change the response time of the course as it POSTs more threads
    than it DELETEs. As the course becomes larger, the response times become
    slower (assuming

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
            "roles": ["Administrator"]
        }
        self.auto_auth(verify_ssl=False, params=params)

    tasks = {
        #DeleteCommentsTask: 40,
        #DeleteThreadsTask: 40,
        #GetThreadsTask: 7560,
        #PatchCommentsTask: 83,
        #PatchThreadsTask: 92,
        #PostCommentsTask: 194,
        #PostThreadsTask: 220,
        #GetCommentsTask: 2000,
        #GetThreadsTask: 88000,
        #PatchCommentsTask: 92,
        #PatchThreadsTask: 69,
        #PostCommentsTask: 300,
        #PostThreadsTask: 200,
    }

class DiscussionsApiLocust(HttpLocust):
    task_set = globals()[os.getenv('LOCUST_TASK_SET', 'DiscussionsApiTest')]
    min_wait = int(os.getenv('LOCUST_MIN_WAIT', 5000))
    max_wait = int(os.getenv('LOCUST_MAX_WAIT', 5000))
    #min_wait = int(os.getenv('LOCUST_MIN_WAIT', 1000))
    #max_wait = int(os.getenv('LOCUST_MAX_WAIT', 2000))
    #min_wait = max_wait = 500
