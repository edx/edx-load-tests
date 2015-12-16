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
from forums import ForumsTasks
from lms import LmsTasks
from module_render import ModuleRenderTasks


class LmsTest(LmsTasks):
    """
    TaskSet that pulls together all the LMS-related TaskSets into a single unified test.

    Traffic Distribution on courses.edx.org (last 7d as of 2014-02-24):

    0.14%   /branding.views Total
    0.00%   /certificates.views Total
    11.24%  /contentserver.middleware Total
    0.27%   /course_modes.views Total
    0.00%   /course_wiki.middleware Total
    0.02%   /course_wiki.views Total
    0.00%   /courseware.masquerade Total
    27.11%  /courseware.module_render Total  (ModuleRenderTasks)
    8.59%   /courseware.views Total   (CoursewareViewsTasks)
    0.00%   /dashboard.support Total
    0.10%   /django_comment_client.base.views Total  (ForumsTasks)
    0.93%   /django_comment_client.forum.views Total  (ForumsTasks)
    0.00%   /django.contrib.admin.options Total
    0.00%   /django.contrib.admin.sites Total
    0.02%   /django.contrib.auth.views Total
    0.00%   /django.core.handlers.wsgi Total
    0.02%   /django.middleware.common Total
    0.10%   /django.middleware.csrf Total
    0.00%   /django.views.defaults Total
    0.03%   /django.views.generic.base Total
    0.00%   /django.views.generic.edit Total
    0.00%   /django.views.generic.list Total
    6.72%   /django.views.i18n Total
    0.01%   /edxval.views Total
    0.00%   /embargo.middleware Total
    0.03%   /enrollment.views Total
    0.09%   /external_auth.views Total
    8.56%   /heartbeat.views Total
    0.00%   /instructor_task.views Total
    0.84%   /instructor.views.api Total
    0.05%   /instructor.views.instructor_dashboard Total
    0.00%   /instructor.views.legacy Total
    0.01%   /lang_pref.views Total
    0.02%   /mobile_api.course_info.views Total
    0.13%   /mobile_api.users.views Total
    0.15%   /mobile_api.video_outlines.views Total
    0.00%   /notes.views Total
    0.11%   /notification_prefs.views Total
    0.03%   /notifier_api.views Total
    0.00%   /oauth2_provider.views Total
    0.00%   /open_ended_grading.staff_grading_service Total
    0.01%   /open_ended_grading.views Total
    0.00%   /openedx.core.djangoapps.course_groups.views Total
    1.82%   /openedx.core.djangoapps.user_api.views Total
    0.00%   /provider.oauth2.views Total
    0.02%   /provider.views Total
    0.01%   /rest_framework.decorators Total
    0.00%   /shoppingcart.decorators Total
    0.01%   /shoppingcart.views Total
    0.19%   /social.apps.django_app.views Total
    0.89%   /static_template_view.views Total
    0.05%   /staticbook.views Total
    0.14%   /student_account.views Total
    0.00%   /student.middleware Total
    1.68%   /student.views Total
    0.00%   /survey.views Total
    29.43%  /track.views Total
    0.38%   /track.views.segmentio Total
    0.01%   /util.views Total
    0.05%   /verify_student.views Total
    0.00%   /wiki.decorators Total
    0.00%   /wiki.views.article Total

    """

    tasks = {
        CoursewareViewsTasks: 9,
        ForumsTasks: 2,
        ModuleRenderTasks: 27,
    }


class LmsLocust(HttpLocust):
    task_set = globals()[os.getenv('LOCUST_TASK_SET', 'LmsTest')]
    min_wait = int(os.getenv('LOCUST_MIN_WAIT', 7500))
    max_wait = int(os.getenv('LOCUST_MAX_WAIT', 15000))
