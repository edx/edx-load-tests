import random
import re

from locust import task

from base import LmsTasks


class ModuleRenderTasks(LmsTasks):
    """
    Tests callback handlers implemented in lms.djangoapps.courseware.module_render

    See util/lms_module_render_tx_distribution.sh for instructions on
    generating the data below.

    module_render endpoint distribution (last 7 days as of 2015-02-25):

    /XBlock/Handler/VideoDescriptorWithMixins.transcript,29.83%
    /XBlock/Handler/VideoDescriptorWithMixins.xmodule_handler/save_user_state,22.49%
    /XBlock/Handler/SequenceDescriptorWithMixins.xmodule_handler/goto_position,15.70%
    /XBlock/Handler/CapaDescriptorWithMixins.xmodule_handler/input_ajax,11.64%  (TODO: see [0])
    /XBlock/Handler/CapaDescriptorWithMixins.xmodule_handler/problem_check,9.75%
    /XBlock/Handler/CapaDescriptorWithMixins.xmodule_handler/problem_show,2.07%
    /XBlock/Handler/DragAndDropBlockWithMixins.publish_event,1.93%
    /XBlock/Handler/DragAndDropBlockWithMixins.drop_item,0.60%
    /XBlock/Handler/LTIDescriptorWithMixins.grade_handler,0.49%
    /XBlock/Handler/LtiConsumerXBlockWithMixins.outcome_service_handler,0.39%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.render_self_assessment,0.35%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.render_peer_assessment,0.34%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.render_grade,0.34%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.render_student_training,0.34%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.render_message,0.34%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.render_leaderboard,0.34%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.render_staff_assessment,0.34%
    /XBlock/Handler/CapaDescriptorWithMixins.xmodule_handler/problem_get,0.32%
    /XBlock/Handler/CapaDescriptorWithMixins.xmodule_handler/problem_save,0.28%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.render_submission,0.27%
    /XBlock/Handler/CapaDescriptorWithMixins.xmodule_handler/problem_reset,0.25%
    /XBlock/Handler/LTIDescriptorWithMixins.preview_handler,0.24%
    /XBlock/Handler/DragAndDropBlockWithMixins.get_user_state,0.18%
    /XBlock/Handler/LtiConsumerXBlockWithMixins.lti_launch_handler,0.10%
    /XBlock/Handler/PollBlockWithMixins.student_voted,0.10%
    /XBlock/Handler/DragAndDropBlockWithMixins.do_attempt,0.10%
    /XBlock/Handler/WordCloudDescriptorWithMixins.xmodule_handler/get_state,0.08%
    /XBlock/Handler/SchoolYourselfReviewXBlockWithMixins.handle_grade,0.08%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.save_submission,0.08%
    /XBlock/Handler/SplitTestDescriptorWithMixins.log_child_render,0.07%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.peer_assess,0.06%
    /XBlock/Handler/PollBlockWithMixins.get_results,0.06%
    /XBlock/Handler/ConditionalDescriptorWithMixins.xmodule_handler/conditional_get,0.05%
    /XBlock/Handler/CapaDescriptorWithMixins.xmodule_handler/hint_button,0.04%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/get_state,0.04%
    /XBlock/Handler/PollBlockWithMixins.vote,0.03%
    /XBlock/Handler/SurveyBlockWithMixins.student_voted,0.03%
    /XBlock/Handler/DoneXBlockWithMixins.toggle_button,0.03%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.submit,0.03%
    /XBlock/Handler/WordCloudDescriptorWithMixins.xmodule_handler/submit,0.03%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.self_assess,0.02%
    /XBlock/Handler/AnswerBlockWithMixins.answer_value,0.01%
    /XBlock/Handler/MentoringBlockWithMixins.publish_event,0.01%
    /XBlock/Handler/MentoringBlockWithMixins.get_results,0.01%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.upload_url,0.01%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.download_url,0.01%
    /XBlock/Handler/SurveyBlockWithMixins.vote,0.01%
    /XBlock/Handler/PeerInstructionXBlockWithMixins.get_data,0.01%
    /XBlock/Handler/SurveyBlockWithMixins.get_results,0.01%
    /XBlock/Handler/GoogleDocumentBlockWithMixins.publish_event,0.01%
    /XBlock/Handler/GoogleCalendarBlockWithMixins.publish_event,0.01%
    /XBlock/Handler/MentoringBlockWithMixins.submit,0.01%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.render_staff_area,0.01%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.submit_feedback,0.01%
    /XBlock/Handler/PeerInstructionXBlockWithMixins.submit_answer,0.01%
    /XBlock/Handler/PeerInstructionXBlockWithMixins.get_stats,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/yes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/no,0.00%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.training_assess,0.00%
    /XBlock/Handler/DragAndDropBlockWithMixins.reset,0.00%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.render_student_info,0.00%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.render_staff_grade_counts,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/reset_poll,0.00%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.render_staff_grade_form,0.00%
    /XBlock/Handler/DragAndDropBlockWithMixins.show_answer,0.00%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.staff_assess,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Absolutely,0.00%
    /XBlock/Handler/SequenceDescriptorWithMixins.xmodule_handler,0.00%
    /XBlock/Handler/SequenceDescriptorWithMixins.,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/king,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/not_ace,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/To a great extent,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Yes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/2,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/stairs,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/perception,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/coping,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/learning,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/No,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/tellMe,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/agree,0.00%
    /XBlock/Handler/OppiaXBlockWithMixins.on_state_transition,0.00%
    /XBlock/Handler/MentoringBlockWithMixins.view,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/4,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/3,0.00%
    /XBlock/Handler/OppiaXBlockWithMixins.on_exploration_loaded,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/disagree,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/other,0.00%
    /XBlock/Handler/AnswerRecapBlockWithMixins.refresh_html,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/5,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/heart,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/To a little extent,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/health,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/confident,0.00%
    /XBlock/Handler/RecommenderXBlockWithMixins.export_resources,0.00%
    /XBlock/Handler/OpenAssessmentBlockWithMixins.cancel_submission,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Level 4,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Awareness based change,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/actual,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Level 2,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/stud,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/development,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/no_watch,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/bachelor,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Collective creativity,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/not,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/burnout,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/low,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Dialogue,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/master,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/howDid,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Divisionalized,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Eco systemic,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Downloading,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Competition,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/0,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/yes_pilot,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Networked,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/face,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Level 3,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/escalator,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/week_1_poll_1_yes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/a,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/howCan,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Hierarchy,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Not at all confident,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Centralized,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/professional,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/whatCan,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Cyes,0.00%
    /XBlock/Handler/OfficeMixXBlockWithMixins.publish_event,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Bno,0.00%
    /XBlock/Handler/OppiaXBlockWithMixins.on_exploration_completed,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Ano,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/E,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/3.2a,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Debate,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/highschool,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/6,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/8,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/2-5no,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/2-6no,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Eno,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Hno,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/yes_owner,0.00%
    /XBlock/Handler/RecommenderXBlockWithMixins.add_resource,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Dyes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Not at all,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Fno,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/phd,0.00%
    /XBlock/Handler/RecommenderXBlockWithMixins.flag_resource,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6-76-125,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Gyes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/week_6_poll_2_yes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/3.3a,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/c,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Gno,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-2yes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/week_6_poll_1_yes,0.00%
    /XBlock/Handler/VideoDescriptorWithMixins.,0.00%
    /XBlock/Handler/LTIDescriptorWithMixins.preview_handler&quot;,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Slowburn,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/week_2_poll_1_no,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/d,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/B,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/na,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/3.1a,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/yes1,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/D,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/3-3yes,0.00%
    /XBlock/Handler/SequenceDescriptorWithMixins.pvkohut@gmail.com,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/policy,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Level 1,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/7.4c,0.00%
    /XBlock/Handler/SequenceDescriptorWithMixins.bam.nr-data.net,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/week_6_poll_3_yes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/vit1,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/week_1_poll_2_yes,0.00%
    /XBlock/Handler/SequenceDescriptorWithMixins.js-agent.newrelic.com,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/A,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/2-6yes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/Stakeholder negotiation,0.00%
    /XBlock/Handler/SequenceDescriptorWithMixins.bugs@edx.org,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6-0-25,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/2-7Ano,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Ayes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/2-5yes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/7.2b,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/2.1a,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/none,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Hyes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/7.3d,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/3-7Byes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/3-7Ayes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/2-7Bno,0.00%
    /XBlock/Handler/RecommenderXBlockWithMixins.handle_vote,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/33-4no,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/7.9a,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/33-3no,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/2-7Cyes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/2-7Cno,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/2.1b,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/practice,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/4.1a,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/sweetened,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Fyes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Dno,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6Eyes,0.00%
    /XBlock/Handler/PollDescriptorWithMixins.xmodule_handler/1-6-26-75,0.00%

    [0] We should change the demo course to include a formula input problem so
        we can hit it with the /input_ajax endpoint.
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

    @task(16)
    def goto_position(self):
        """
        POST to goto_position in our course, using random inputs based on course data.
        """
        self.post(
            self._handler_path('sequential', self.course_data.sequential_id, 'xmodule_handler/goto_position'),
            data={'position': unicode(random.randint(0, 10))},
            name='handler:goto_position',
        )

    @task(1)
    def capa_problem_get(self):
        """
        Exercise the problem_get handler.
        """
        self._post_capa_handler('problem_get')

    @task(2)
    def capa_problem_show(self):
        """
        Exercise the problem_show handler.
        """
        self._post_capa_handler('problem_show')

    @task(10)
    def capa_problem_check(self):
        """
        Exercise the problem_check handler.
        """
        self._post_capa_handler('problem_check')

    @task(1)
    def capa_problem_save(self):
        """
        Exercise the problem_save handler.
        """
        self._post_capa_handler('problem_save')

    @task(30)
    def get_transcript(self):
        """
        Exercises transcript retrieval, using random inputs based on course data.
        """
        self.get(
            self._handler_path('video', self.course_data.video_module_id, 'transcript/translation/en'),
            params={'videoId': self.course_data.video_id},
            name="handler:video:get_transcript"
        )

    @task(22)
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

    @task(9)
    def stop(self):
        """
        Switch to another TaskSet.
        """
        self.interrupt()
