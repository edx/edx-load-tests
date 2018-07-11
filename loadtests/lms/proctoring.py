import json
from locust import task

from base import LmsTasks


class ProctoredExamTasks(LmsTasks):
    """
    Tasks representing the accessing of the proctored exam endpoints.

    These endpoints are used by both timed exams and proctored exams to sync the
    browser state with the server state. Both proctored exams and timed exams
    share their code.
    """

    attempt_id = None
    attempt_api_path = '/api/edx_proctoring/v1/proctored_exam/attempt'

    def on_start(self):
        super(ProctoredExamTasks, self).on_start()
        self.create_attempt()

    def create_attempt(self):
        """
        Create an attempt for the current user.
        """
        data = {'exam_id': self.course_data.exam_id, 'start_clock': True}
        response = self.client.post(self.attempt_api_path, data=data, headers=self.post_headers)
        response_data = json.loads(response.text)
        self.attempt_id = response_data.get('exam_attempt_id')

    @task(9)
    def exam_poll_attempt(self):
        """
        Retrieves the status of an existing exam attempt.

        This mimics the polling that the banner of a timed exam or proctored exam performs.
        """
        attempt_id = self.attempt_id

        self.client.get(
            '{url}/{attempt_id}'.format(url=self.attempt_api_path, attempt_id=attempt_id),
            name='timed_exam:poll_attempt'
        )

    @task(1)
    def stop(self):
        """
        Switch to another TaskSet.
        """
        self.interrupt()
