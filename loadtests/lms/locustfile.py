"""
Load test for the edx-platform LMS.
"""
import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from locust import HttpLocust

from authentication_views import AuthenticationViewsTasks
from courseware_views import CoursewareViewsTasks
from forums import ForumsTasks, SeedForumsTasks
from base import LmsTasks
from proctoring import ProctoredExamTasks
from module_render import ModuleRenderTasks
from wiki_views import WikiViewTask
from tracking import TrackingTasks
from helpers import settings, markers

settings.init(__name__, required_data=[
    'courses',
    'LOCUST_TASK_SET',
    'LOCUST_MIN_WAIT',
    'LOCUST_MAX_WAIT',
])

markers.install_event_markers()


class LmsTest(LmsTasks):
    """
    TaskSet that pulls together all the LMS-related TaskSets into a single unified test.

    See util/lms_tx_distribution.sh for instructions on generating the data
    below.

    Traffic Distribution on courses.edx.org (last 7d as of 2016-11-16):

    /openedx.core.djangoapps.heartbeat.views Total, 26.34%
    /track.views Total, 24.24%  (TrackingTasks)
    /courseware.module_render Total, 21.74%  (ModuleRenderTasks)
    /enrollment.views Total, 3.60%
    /courseware.views.index Total, 3.22%  (CoursewareViewsTasks)
    /track.views.segmentio Total, 2.92%
    /openedx.core.djangoapps.contentserver.middleware Total, 2.77%
    /branding.views Total, 1.95%
    /edxnotes.views Total, 1.75%
    /corsheaders.middleware Total, 1.60%
    /openedx.core.djangoapps.user_api.views Total, 1.52%
    /courseware.views.views Total, 1.33%  (CoursewareViewsTasks)
    /student.views Total, 1.09%
    /lms.djangoapps.instructor.views.api Total, 0.85%
    /discussion.views Total, 0.65%  (ForumsTasks)
    /mobile_api.users.views Total, 0.56%
    /edx_proctoring.views Total, 0.41%
    /openedx.core.djangoapps.user_api.accounts.views Total, 0.37%
    /course_modes.views Total, 0.34%
    /openedx.core.djangoapps.performance.views Total, 0.27%
    /django.middleware.common Total, 0.23%
    /social.apps.django_app.views Total, 0.21%
    /commerce.api.v0.views Total, 0.21%
    /student_account.views Total, 0.20%
    /openedx.core.djangoapps.theming.middleware Total, 0.20%
    /openedx.core.djangoapps.external_auth.views Total, 0.17%
    /openedx.core.djangoapps.oauth_dispatch.views Total, 0.16%
    /discussion_api.views Total, 0.11%  (ForumsTasks)
    /openedx.core.djangoapps.user_api.preferences.views Total, 0.10%
    /openedx.core.djangoapps.cors_csrf.middleware Total, 0.08%
    /mobile_api.video_outlines.views Total, 0.08%
    /notification_prefs.views Total, 0.07%
    /notifier_api.views Total, 0.06%
    /django_comment_client.base.views Total, 0.06%  (ForumsTasks)
    /openedx.core.djangoapps.bookmarks.views Total, 0.05%
    /learner_dashboard.views Total, 0.05%
    /course_api.blocks.views Total, 0.05%
    /openedx.core.djangoapps.auth_exchange.views Total, 0.04%
    /staticbook.views Total, 0.03%
    /lms.djangoapps.verify_student.views Total, 0.03%
    /edxval.views Total, 0.03%
    /certificates.views.webview Total, 0.03%
    /student_profile.views Total, 0.02%
    /rest_framework.decorators Total, 0.02%
    /provider.oauth2.views Total, 0.02%
    /edx_oauth2_provider.views Total, 0.02%
    /wiki.views.article Total, 0.01%
    /util.views Total, 0.01%
    /third_party_auth.views Total, 0.01%
    /static_template_view.views Total, 0.01%
    /openedx.core.djangoapps.safe_sessions.middleware Total, 0.01%
    /openedx.core.djangoapps.course_groups.views Total, 0.01%
    /mobile_api.course_info.views Total, 0.01%
    /lms.djangoapps.teams.views Total, 0.01%
    /lms.djangoapps.certificates.apis.v0.views Total, 0.01%
    /django.contrib.auth.views Total, 0.01%
    /course_api.views Total, 0.01%
    /commerce.views Total, 0.01%
    /commerce.api.v1.views Total, 0.01%
    /wiki.decorators Total, 0.00%
    /verified_track_content.views Total, 0.00%
    /survey.views Total, 0.00%
    /support.views.programs Total, 0.00%
    /support.views.index Total, 0.00%
    /support.views.enrollments Total, 0.00%
    /support.views.certificate Total, 0.00%
    /shoppingcart.views Total, 0.00%
    /shoppingcart.decorators Total, 0.00%
    /rss_proxy.views Total, 0.00%
    /ratelimitbackend.admin Total, 0.00%
    /organizations.v0.views Total, 0.00%
    /openedx.core.djangoapps.profile_images.views Total, 0.00%
    /openedx.core.djangoapps.credit.views Total, 0.00%
    /openedx.core.djangoapps.cors_csrf.views Total, 0.00%
    /openedx.core.djangoapps.api_admin.views Total, 0.00%
    /lms.djangoapps.instructor.views.instructor_dashboard Total, 0.00%
    /lms.djangoapps.grades.api.views Total, 0.00%
    /embargo.views Total, 0.00%
    /embargo.middleware Total, 0.00%
    /edx_proctoring.callbacks Total, 0.00%
    /django.views.i18n Total, 0.00%
    /django_sites_extensions.middleware Total, 0.00%
    /django.middleware.csrf Total, 0.00%
    /django.core.handlers.wsgi Total, 0.00%
    /django.contrib.admin.sites Total, 0.00%
    /django.contrib.admin.options Total, 0.00%
    /course_wiki.views Total, 0.00%
    /course_wiki.middleware Total, 0.00%
    /courseware.masquerade Total, 0.00%
    /course_structure_api.v0.views Total, 0.00%
    /config_models.views Total, 0.00%
    /certificates.views.xqueue Total, 0.00%
    /certificates.views.support Total, 0.00%
    /ccx.views Total, 0.00%

    """

    tasks = {
        AuthenticationViewsTasks: 1,
        CoursewareViewsTasks: 5,
        ForumsTasks: 1,
        ModuleRenderTasks: int(round(22 * float(settings.data.get('MODULE_RENDER_MODIFIER', 1)))),
        ProctoredExamTasks: int(round(1 * float(settings.data.get('PROCTORED_EXAM_MODIFIER', 1)))),
        TrackingTasks: 24,
    }


class LmsLocust(HttpLocust):
    task_set = globals()[settings.data['LOCUST_TASK_SET']]
    min_wait = settings.data['LOCUST_MIN_WAIT']
    max_wait = settings.data['LOCUST_MAX_WAIT']

    def __init__(self, *args, **kwargs):
        super(LmsLocust, self).__init__(*args, **kwargs)
        self._user_id = None
        self._email = None
        self._password = None
        self._is_logged_in = False
        self._is_enrolled = False

    @property
    def _is_registered(self):
        return bool(self._user_id and self._email and self._password)
