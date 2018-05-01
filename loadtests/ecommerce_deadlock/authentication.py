import uuid

from locust import TaskSet

from helpers import settings

LMS_HOST = settings.data['LMS_HOST'].rstrip('\/')


class AuthenticationMixin(TaskSet):
    """Mixin that gives tasks different authentication methods."""

    def __init__(self, parent):
        super().__init__(parent)
        self._setup_basic_auth()

    def on_start(self):
        """Raise an exception. This TaskSet is not meant to be run on its own."""
        raise Exception("This TaskSet is not meant to be run")

    def auto_auth_login(self):
        """Create a new account with given credentials and log in.

        This requires that the test server has the feature flag
        `AUTOMATIC_AUTH_FOR_TESTING` set to True.
        """
        auto_auth_username = "ecom_deadlock"
        auto_auth_email_url = "simulator.amazonses.com"
        default_password = "test"

        del self.client.cookies["sessionid"]
        username = "{0}{1}".format(auto_auth_username, uuid.uuid4().hex[:20])
        full_email = "{0}@{1}".format(username, auto_auth_email_url)
        params = {
            'password': default_password,
            'email': full_email,
            'username': username,
        }

        self.client.get("/auto_auth", params=params, verify=False, name="/auto_auth")

    def login(self, email, password):
        """
        Login to the LMS for the given credentials

        Args:
            email (str): User email
            password (str): User's password

        """
        signin_url = '{}/login'.format(LMS_HOST)
        headers = self._get_csrf(signin_url)
        login_url = '{}/login_ajax'.format(LMS_HOST)
        response = self.client.post(login_url, {
            'email': email,
            'password': password,
            'honor_code': 'true'
        }, headers=headers).json()
        if not response['success']:
            raise Exception(str(response))
        print('Login successful {}'.format(email))

    def _get_csrf(self, url):
        try:
            response = self.client.get(url)
            csrf = response.cookies['csrftoken']
            return {'X-CSRFToken': csrf, 'Referer': url}
        except Exception as error:  # pylint: disable=W0703
            print("Error when retrieving csrf token.", error)

    def _setup_basic_auth(self):
        """Sets up basic authentication if available"""
        if settings.data.get('BASIC_AUTH') is not None:
            self.client.auth = (
                settings.data['BASIC_AUTH']['BASIC_AUTH_USER'],
                settings.data['BASIC_AUTH']['BASIC_AUTH_PASS'],
            )
