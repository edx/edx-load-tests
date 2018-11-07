
from locust import task
from base import LmsTasks


class GenerateGradeReportTask(LmsTasks):
    """
    A very simple task that will hit one of instructor dashboard api
    to generate course grade csv.
    """
    def on_start(self):
        params = {
            "course_id": self.course_id,
            "staff": "true",
            "roles": ["Administrator"],
        }
        self.auto_auth(verify_ssl=False, params=params)

    @task
    def generate_report(self):
        """
        Request (post) to the api endpoint to generate csv.
        """
        path = 'instructor/api/calculate_grades_csv'
        self.post(path, name='instructor_dashboard:grade_csv')
