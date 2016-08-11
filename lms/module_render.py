import random
import re

from locust import task

from lms.base import LmsTasks


class ModuleRenderTasks(LmsTasks):
    """
    Tests callback handlers implemented in lms.djangoapps.courseware.module_render

    NewRelic reports virtually all of this traffic under the single function call,
    module_render.handle_xblock_callback.   The following list of top endpoints
    comes from a rough analysis of access logs for the 7 days prior to 2015-02-25.

    xmodule_handler/problem_get      5157055  21.22%
    xmodule_handler/save_user_state  5144295  21.17%
    xmodule_handler/goto_position    3207403  13.20%
    xmodule_handler/input_ajax       2597538  10.69%
    transcript/translation/en        2306780  9.49%
    xmodule_handler/problem_check    1969296  8.10%
    goto_position                    538610   2.22%
    xmodule_handler/problem_show     466705   1.92%
    save_user_state                  447787   1.84%
    handle_grade                     291978   1.20%
    problem_get                      244093   1.00%
    xmodule_handler/problem_save     226407   0.93%
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

        def format_input_key(key):
            return 'input_i4x-{{course_org}}-{{course_num}}-problem-{}'.format(problem_id) + key

        problem_id, problem_data, problem_input = self.course_data.capa_problem
        if handler == 'problem_show' and problem_data.get('showanswer', 'never') != 'always':
            # gonna fail
            return
        if handler in ('problem_save', 'problem_check'):
            data = {format_input_key(key): value for key, value in problem_input.iteritems()}
        else:
            data = None
        self.post(
            self._handler_path('problem', problem_id, 'xmodule_handler/{}'.format(handler)),
            data=data,
            name='handler:capa:{}'.format(handler),
        )

    @task(13)
    def goto_position(self):
        """
        POST to goto_position in our course, using random inputs based on course data.
        """
        self.post(
            self._handler_path('sequential', self.course_data.sequential_id, 'xmodule_handler/goto_position'),
            data={'position': unicode(random.randint(0, 10))},
            name='handler:goto_position',
        )

    @task(22)
    def capa_problem_get(self):
        """
        Exercise the problem_get handler.
        """
        return self._post_capa_handler('problem_get')

    @task(2)
    def capa_problem_show(self):
        """
        Exercise the problem_show handler.
        """
        return self._post_capa_handler('problem_show')

    @task(8)
    def capa_problem_check(self):
        """
        Exercise the problem_check handler.
        """
        return self._post_capa_handler('problem_check')

    @task(1)
    def capa_problem_save(self):
        """
        Exercise the problem_save handler.
        """
        return self._post_capa_handler('problem_save')

    @task(9)
    def get_transcript(self):
        """
        Exercises transcript retrieval, using random inputs based on course data.
        """
        self.get(
            self._handler_path('video', self.course_data.video_module_id, 'transcript/translation/en'),
            params={'videoId': self.course_data.video_id},
            name="handler:video:get_transcript"
        )

    @task(20)
    def save_user_state(self):
        """
        Exercises user state persistence, using random inputs based on course data.
        """
        data = random.choice([
            {'youtube_is_available': random.choice(['true', 'false'])},
            {'saved_video_position': random.choice(['00:00:00', '01:23:45', '02:46:08'])},
        ])
        self.post(
            self._handler_path('video', self.course_data.video_module_id, 'xmodule_handler/save_user_state'),
            data=data,
            name="handler:video:save_user_state"
        )
