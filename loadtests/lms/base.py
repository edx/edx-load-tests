"""
"""

import logging

from helpers.edx_app import EdxAppTasks
from helpers.mixins import EnrollmentTaskSetMixin
from helpers import settings
from urlparse import urlparse


class LmsTasks(EnrollmentTaskSetMixin, EdxAppTasks):
    """
    Base class for course-specific LMS TaskSets.
    """

    def _request(self, method, path, *args, **kwargs):
        """
        Single internal helper for setting up course-specific LMS requests.
        """
        self.client.cookies.clear(domain=urlparse(self.client.base_url).hostname, path='/', name='AWSELB')
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
