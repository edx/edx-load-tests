"""
"""

import logging

from lazy import lazy
from opaque_keys.edx.keys import CourseKey

import course_data
from helpers import settings, util
from helpers.auto_auth_tasks import AutoAuthTasks
from helpers.mixins import EnrollmentTaskSetMixin, HeadersTaskSetMixin


class EdxAppTasks(HeadersTaskSetMixin, AutoAuthTasks):
    """
    Methods useful to any/all HTTP tests for edx-platform (i.e. LMS or Studio).
    """

    @lazy
    def course_id(self):
        """
        The complete id of the course we're configured to test with.

        This function is evaluated once per locust client and its return value
        is cached on a per-client basis (due to the @lazy decorator).  It
        randomly selects a course from the "courses" dict specified in the
        settings file.  The "ratio" keys of every course are used to construct
        a probability distribution.
        """
        courses = settings.data['courses']
        course_ratio_pairs = \
            [(cid, cdata['ratio']) for cid, cdata in courses.iteritems()]
        return util.choice_with_distribution(course_ratio_pairs)

    @lazy
    def course_key(self):
        """
        The course_id.
        """
        return CourseKey.from_string(self.course_id)

    @lazy
    def course_org(self):
        """
        The 'org' part of the course_id.
        """
        return self.course_key.org

    @lazy
    def course_num(self):
        """
        The 'num' (aka 'course') part of the course_id.
        """
        return self.course_key.course

    @lazy
    def course_run(self):
        """
        The 'run' part of the course_id.
        """
        return self.course_key.run

    @lazy
    def course_data(self):
        """
        Accessor for the CourseData instance we're configured to test with.
        """
        course_data_name = self._get_course_setting('course_data')
        return getattr(course_data, course_data_name)

    def _get_course_setting(self, setting):
        """
        Accessor for a setting specific to the current course.

        Args:
            setting (str): name of course-specific setting

        Raises:
            KeyError: If the setting was not specified for this locust client's
                selected course_id.
        """
        return settings.data['courses'][self.course_id][setting]


class LmsTasks(EnrollmentTaskSetMixin, EdxAppTasks):
    """
    Base class for course-specific LMS TaskSets.

    This class supports the following settings:

    * COURSE_ID: pass the course_id against which requests should be made.
    * COURSE_DATA: pass the name of a CourseData object, which should be
      importable from the `course_data` subpackage.  Obviously, the id and the
      data should correlate, or you're likely to see a high error rate in your
      results.
    """

    def _request(self, method, path, *args, **kwargs):
        """
        Single internal helper for setting up course-specific LMS requests.
        """
        path = '/courses/{course_id}/' + path
        path = path.format(**{n: getattr(self, n) for n in ('course_id', 'course_num', 'course_run', 'course_org')})
        logging.debug(path)
        return getattr(self.client, method)(path, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Perform a GET, contextualizing the path for the course under test.

        String formatting placeholders for 'course_id', 'course_num', 'course_run', 'course_org'
        in the passed path will be evaluated and replaced.
        """
        return self._request('get', *args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Perform a POST, contextualizing the path for the course under test, and adding any
        mandatory request headers not explicitly passed in the call.

        String formatting placeholders for 'course_id', 'course_num', 'course_run', 'course_org'
        in the passed path will be evaluated and replaced.
        """
        headers = self.post_headers
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers
        return self._request('post', *args, **kwargs)

    def on_start(self):
        self.auto_auth()
        self.enroll(self.course_id)
