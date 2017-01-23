"""
Load test for the edx-platform LMS.
"""
import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from locust import HttpLocust

from courseware_views import CoursewareViewsTasks
from forums import ForumsTasks, SeedForumsTasks
from base import LmsTasks
from proctoring import ProctoredExamTasks
from module_render import ModuleRenderTasks
from wiki_views import WikiViewTask
from tracking import TrackingTasks

from helpers import settings
settings.init(__name__, required_data=[
    'COURSE_ID',
    'COURSE_DATA',
    'LOCUST_TASK_SET',
    'LOCUST_MIN_WAIT',
    'LOCUST_MAX_WAIT',
])


class LmsTest(LmsTasks):
    """
    TaskSet that has ben hijacked by Eric and Sandy
    """

    tasks = {
        ModuleRenderTasks: 1
    }


class LmsLocust(HttpLocust):
    task_set = globals()[settings.data['LOCUST_TASK_SET']]
    min_wait = settings.data['LOCUST_MIN_WAIT']
    max_wait = settings.data['LOCUST_MAX_WAIT']
