"""
Load test for the edx-platform LMS.

Usage:

  $ locust --host="http://localhost:8000"

Supported Environment Variables:

  BASIC_AUTH_USER, BASIC_AUTH_PASS - if set, will use for HTTP Authentication
  LOCUST_TASK_SET - if set, will run the specified TaskSet (must be imported in this module)
  LOCUST_MIN_WAIT, LOCUST_MAX_WAIT - use to override defaults set in this module
  COURSE_ID - course that will be tested on the target host, default is set in lms.LmsTasks
  COURSE_DATA - course_data module that will be used for parameters, default is set in lms.LmsTasks

"""
import os

from locust import HttpLocust

from courseware_views import CoursewareViewsTasks
from lms import LmsTasks


class LmsTest(LmsTasks):
    """
    ALL YOUR TASK ARE BELONG TO US
    """

    tasks = CoursewareViewsTasks


class LmsLocust(HttpLocust):
    task_set = globals()[os.getenv('LOCUST_TASK_SET', 'LmsTest')]
    min_wait = int(os.getenv('LOCUST_MIN_WAIT', 7500))
    max_wait = int(os.getenv('LOCUST_MAX_WAIT', 15000))
