"""
Load test for the Discussions API

Usage:

  $ locust --host="http://localhost:8000"

Supported Environment Variables:

  BASIC_AUTH_USER, BASIC_AUTH_PASS - if set, will use for HTTP Authentication
  LOCUST_TASK_SET - if set, will run the specified TaskSet (must be imported in this module)
  COURSE_ID - course that will be tested on the target host, default is set in lms.LmsTasks
  SEEDED_DATA - rqeuired for the GET Thread test

"""
import os

from locust import HttpLocust

from discussions_api import DiscussionsApiTasks
from tasks.dapi_tasks import (
    DeleteCommentsTask,
    DeleteThreadsTask,
    GetCommentsTask,
    GetThreadsTask,
    PatchCommentsTask,
    PatchThreadsTask,
    PostCommentsTask,
    PostThreadsTask,
)


class DiscussionsApiTest(DiscussionsApiTasks):

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
        # DeleteCommentsTask: 40,
        # DeleteThreadsTask: 40,
        GetCommentsTask: 2000,
        GetThreadsTask: 7560,
        # PatchCommentsTask: 83,
        #PatchThreadsTask: 92,
        #PostCommentsTask: 194,
        #PostThreadsTask: 220,
    }

class DiscussionsApiLocust(HttpLocust):
    task_set = globals()[os.getenv('LOCUST_TASK_SET', 'DiscussionsApiTest')]
    min_wait = int(os.getenv('LOCUST_MIN_WAIT', 1000))
    max_wait = int(os.getenv('LOCUST_MAX_WAIT', 2000))
    min_wait = max_wait = 500
