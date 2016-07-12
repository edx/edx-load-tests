import os
import requests

BASIC_AUTH_CREDENTIALS = None
if 'BASIC_AUTH_USER' in os.environ and 'BASIC_AUTH_PASSWORD' in os.environ:
    BASIC_AUTH_CREDENTIALS = (
        os.environ['BASIC_AUTH_USER'],
        os.environ['BASIC_AUTH_PASSWORD']
    )


class Seeder(object):

    def __init__(self, lms_url=None, studio_url=None):
        self.lms_url = lms_url
        self.studio_url = studio_url
        self.sess = requests.Session()
        if BASIC_AUTH_CREDENTIALS is not None:
            self.sess.auth = BASIC_AUTH_CREDENTIALS

    def get_post_headers(self, url, content_type='application/json', accept='application/json'):
        """
        Headers for a POST request, including the CSRF token.
        """
        return {
            'Content-Type': content_type,
            'Accept': accept,
            'X-CSRFToken': self.sess.cookies.get('csrftoken', ''),
            'Referer': url
        }

    def get_csrf(self, url):
        """
        Return csrf token retrieved from the given url.
        """
        try:
            response = self.sess.get(url)
            csrf = response.cookies['csrftoken']
            return {'X-CSRFToken': csrf, 'Referer': url}
        except Exception as error:  # pylint: disable=W0703
            print "Error when retrieving csrf token.", error

    def login(self, email, password, url, signin_path, login_path):
        """
        Use given credentials to login to url (lms or studio).

        Args:
            email (str): Login email
            password (str): Login password
            url (str): Url for lms or studio
            signin_path (str): Url path for sign in (e.g. /login)
            login_path (str): Url path for log in (e.g. /login_post)
        """
        signin_url = '{url}{signin_path}'.format(url=url, signin_path=signin_path)
        headers = self.get_csrf(signin_url)
        login_url = '{url}{login_path}'.format(url=url, login_path=login_path)
        print 'Logging in to {url}'.format(url=url)

        response = self.sess.post(login_url, {
            'email': email,
            'password': password,
            'honor_code': 'true'
        }, headers=headers).json()

        if not response['success']:
            raise Exception(str(response))

        print 'Login successful'

    def login_to_lms(self, email, password):
        """
        Use given credentials to login to studio.

        Attributes:
            email (str): Login email
            password (str): Login password
        """
        if self.lms_url is None:
            raise ValueError("You must supply lms_url to init.")
        self.login(email, password, self.lms_url, '/login', '/login_ajax')

    def login_to_studio(self, email, password):
        """
        Use given credentials to login to studio.

        Attributes:
            email (str): Login email
            password (str): Login password
        """
        if self.studio_url is None:
            raise ValueError("You must supply studio_url to init.")
        self.login(email, password, self.studio_url, '/signin', '/login_post')
