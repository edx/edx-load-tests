from locust import task

from base import LmsTasks


class UserApiViewsTasks(LmsTasks):

    @task(10)
    def login_session(self):
        """
        Test the login_session endpoint.
        """
        if self.locust._is_logged_in:
            self.logout()

        if self.locust._email and self.locust._password:
            self.login(self.locust._email, self.locust._password)

    @task(1)
    def stop(self):
        """
        Switch to a new TaskSet.
        """
        self.interrupt()
