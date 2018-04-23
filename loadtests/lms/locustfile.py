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
from helpers import settings, markers
from user_api_views import UserApiViewsTasks

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

    Traffic Distribution on courses.edx.org (last 7d as of 2018-04-23):

    /track.views Total, 23.67% (TrackingTasks)
    /courseware.module_render Total, 22.67% (ModuleRenderTasks)
    /openedx.core.djangoapps.heartbeat.views Total, 11.37%
    /track.views.segmentio Total, 6.76%
    /experiments.views Total, 4.45%
    /enrollment.views Total, 4.37%
    /courseware.views.index Total, 2.49% (CoursewareViewsTasks)
    /openedx.core.djangoapps.contentserver.middleware Total, 2.35%
    /corsheaders.middleware Total, 2.07%
    /discussion.views Total, 1.76% (ForumsTasks)
    /courseware.views.views Total, 1.76% (CoursewareViewsTasks)
    /edxnotes.views Total, 1.70%
    /branding.views Total, 1.65%
    /mobile_api.users.views Total, 1.21%
    /openedx.core.djangoapps.user_api.validation.views Total, 1.00%
    /openedx.features.course_experience.views.course_home Total, 0.99%
    /student_account.views Total, 0.91%
    /entitlements.api.v1.views Total, 0.73%
    /edx_proctoring.views Total, 0.70%
    /lms.djangoapps.instructor.views.api Total, 0.69%
    /student.views.dashboard Total, 0.68%
    /openedx.core.djangoapps.user_api.views Total, 0.57% (UserApiViewsTasks)
    /openedx.core.djangoapps.user_api.accounts.views Total, 0.49%
    /openedx.core.djangoapps.oauth_dispatch.views Total, 0.41%
    /enterprise.api.v1.views Total, 0.38%
    /django.middleware.common Total, 0.38%
    /discussion_api.views Total, 0.33% (ForumsTasks)
    /mobile_api.video_outlines.views Total, 0.31%
    /course_modes.views Total, 0.31%
    /openedx.core.djangoapps.performance.views Total, 0.25%
    /lms.djangoapps.grades.api.views Total, 0.25%
    /social_django.views Total, 0.22%
    /lms.djangoapps.certificates.apis.v0.views Total, 0.21%
    /openedx.core.djangoapps.user_api.preferences.views Total, 0.19%
    /course_api.blocks.views Total, 0.19%
    /lms.djangoapps.commerce.api.v0.views Total, 0.18%
    /openedx.core.djangoapps.theming.middleware Total, 0.15%
    /openedx.core.djangoapps.auth_exchange.views Total, 0.14%
    /student.views.management Total, 0.12%
    /openedx.features.course_experience.views.course_dates Total, 0.10%
    /edxval.views Total, 0.07%
    /student.views.login Total, 0.06%
    /openedx.core.djangoapps.cors_csrf.middleware Total, 0.06%
    /django_comment_client.base.views Total, 0.06% (ForumsTasks)
    /notifier_api.views Total, 0.05%
    /notification_prefs.views Total, 0.05%
    /lms.djangoapps.course_goals.views Total, 0.05%
    /third_party_auth.api.views Total, 0.04%
    /openedx.core.djangoapps.bookmarks.views Total, 0.04%
    /lms.djangoapps.learner_dashboard.views Total, 0.04%
    /completion.api.v1.views Total, 0.04%
    /openedx.features.course_experience.views.welcome_message Total, 0.03%
    /edx_oauth2_provider.views Total, 0.03%
    /staticbook.views Total, 0.02%
    /provider.oauth2.views Total, 0.02%
    /openedx.features.learner_profile.views.learner_profile Total, 0.02%
    /lms.djangoapps.certificates.views.webview Total, 0.02%
    /django.middleware.csrf Total, 0.02%
    /django.contrib.auth.views Total, 0.02%
    /course_api.views Total, 0.02%
    /wiki.views.article Total, 0.01%
    /third_party_auth.views Total, 0.01%
    /static_template_view.views Total, 0.01%
    /openedx.core.djangoapps.safe_sessions.middleware Total, 0.01%
    /openedx.core.djangoapps.course_groups.views Total, 0.01%
    /mobile_api.course_info.views Total, 0.01%
    /lms.djangoapps.verify_student.views Total, 0.01%
    /lms.djangoapps.discussion.views Total, 0.01%
    /enterprise.views Total, 0.01%
    /wiki.decorators Total, 0.00%
    /util.views Total, 0.00%
    /survey.views Total, 0.00%
    /support.views.refund Total, 0.00%
    /support.views.manage_user Total, 0.00%
    /support.views.index Total, 0.00%
    /support.views.enrollments Total, 0.00%
    /support.views.course_entitlements Total, 0.00%
    /support.views.certificate Total, 0.00%
    /shoppingcart.views Total, 0.00%
    /shoppingcart.decorators Total, 0.00%
    /search.views Total, 0.00%
    /rss_proxy.views Total, 0.00%
    /ratelimitbackend.admin Total, 0.00%
    /organizations.v0.views Total, 0.00%
    /openedx.features.portfolio_project.views Total, 0.00%
    /openedx.features.learner_analytics.views Total, 0.00%
    /openedx.features.course_experience.views.course_updates Total, 0.00%
    /openedx.features.course_experience.views.course_reviews Total, 0.00%
    /openedx.features.course_bookmarks.views.course_bookmarks Total, 0.00%
    /openedx.core.djangoapps.zendesk_proxy.v1.views Total, 0.00%
    /openedx.core.djangoapps.verified_track_content.views Total, 0.00%
    /openedx.core.djangoapps.user_api.verification_api.views Total, 0.00%
    /openedx.core.djangoapps.profile_images.views Total, 0.00%
    /openedx.core.djangoapps.lang_pref.middleware Total, 0.00%
    /openedx.core.djangoapps.external_auth.views Total, 0.00%
    /openedx.core.djangoapps.embargo.views Total, 0.00%
    /openedx.core.djangoapps.embargo.middleware Total, 0.00%
    /openedx.core.djangoapps.credit.views Total, 0.00%
    /openedx.core.djangoapps.cors_csrf.views Total, 0.00%
    /openedx.core.djangoapps.common_views.xblock Total, 0.00%
    /openedx.core.djangoapps.api_admin.views Total, 0.00%
    /openedx.core.djangoapps.api_admin.api.v1.views Total, 0.00%
    /notes.views Total, 0.00%
    /mobile_api.middleware Total, 0.00%
    /lms.djangoapps.teams.views Total, 0.00%
    /lms.djangoapps.support.views.contact_us Total, 0.00%
    /lms.djangoapps.learner_dashboard.programs Total, 0.00%
    /lms.djangoapps.instructor.views.instructor_dashboard Total, 0.00%
    /lms.djangoapps.commerce.views Total, 0.00%
    /lms.djangoapps.commerce.api.v1.views Total, 0.00%
    /lms.djangoapps.certificates.views.support Total, 0.00%
    /enterprise.admin.views Total, 0.00%
    /edx_proctoring.callbacks Total, 0.00%
    /django_object_actions.utils Total, 0.00%
    /django.views.i18n Total, 0.00%
    /django.views.generic.base Total, 0.00%
    /django.contrib.admin.sites Total, 0.00%
    /django.contrib.admin.options Total, 0.00%
    /courseware.masquerade Total, 0.00%
    /course_wiki.views Total, 0.00%
    /course_wiki.middleware Total, 0.00%
    /course_structure_api.v0.views Total, 0.00%
    /consent.api.v1.views Total, 0.00%
    /config_models.admin Total, 0.00%
    /ccx.views Total, 0.00%
    """

    tasks = {
        CoursewareViewsTasks: 5,
        ForumsTasks: 1,
        ModuleRenderTasks: int(round(22 * float(settings.data.get('MODULE_RENDER_MODIFIER', 1)))),
        ProctoredExamTasks: int(round(1 * float(settings.data.get('PROCTORED_EXAM_MODIFIER', 1)))),
        TrackingTasks: 24,
        UserApiViewsTasks: 1
    }


class LmsLocust(HttpLocust):
    task_set = globals()[settings.data['LOCUST_TASK_SET']]
    min_wait = settings.data['LOCUST_MIN_WAIT']
    max_wait = settings.data['LOCUST_MAX_WAIT']

    def __init__(self, *args, **kwargs):
        super(LmsLocust, self).__init__(*args, **kwargs)

        self._email = None
        self._password = None
        self._is_logged_in = False
        self._is_enrolled = False
