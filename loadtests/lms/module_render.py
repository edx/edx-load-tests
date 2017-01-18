import random
import re

from locust import task
import logging

from base import LmsTasks

log = logging.getLogger(__name__)


class ModuleRenderTasks(LmsTasks):
    """
    Tests callback handlers implemented in lms.djangoapps.courseware.module_render

    Hijacked by eric for testing, do not commit me plz
    """

    def _handler_path(self, category, block_id, handler):
        """
        Given category, block_id (display name), and handler name, generate a path
        to invoke the handler via HTTP.
        """
        # based directly on lms runtime implementation. see:
        # https://github.com/edx/edx-platform/blob/master/lms/djangoapps/lms_xblock/runtime.py#L18
        def escape(match):
            matched = match.group(0)
            if matched == ';':
                return ';;'
            elif matched == '/':
                return ';_'
            else:
                return matched

        usage_key = self.course_key.make_usage_key(category, block_id)
        escaped = re.sub(ur'[;/]', escape, unicode(usage_key))
        return "xblock/{}/handler/{}".format(escaped, handler)

    def _post_capa_handler(self, handler):
        """
        Internal helper for formulating valid requests using random inputs based on course data.
        """

        problem_id, problem_data, problem_input = self.course_data.capa_problem
        if handler == 'problem_show' and problem_data.get('showanswer', 'never') != 'always':
            # gonna fail
            return
        if handler in ('problem_save', 'problem_check'):
            data = {
                # the capa handler parses underscores, so this formatting is valid now:
                "LOL_" + problem_id + key: value
                for key, value in problem_input.iteritems()
            }
        else:
            data = None
        self.post(
            self._handler_path('problem', problem_id, 'xmodule_handler/{}'.format(handler)),
            data=data,
            name='handler:capa:{}'.format(handler),
        )

    @task(10)
    def capa_problem_check(self):
        """
        Exercise the problem_check handler.
        """
        self._post_capa_handler('problem_check')
