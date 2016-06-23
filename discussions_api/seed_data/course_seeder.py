import json
import os
import requests
import time

BASIC_AUTH_CREDENTIALS = None
if 'BASIC_AUTH_USER' in os.environ and 'BASIC_AUTH_PASSWORD' in os.environ:
    BASIC_AUTH_CREDENTIALS = (
        os.environ['BASIC_AUTH_USER'],
        os.environ['BASIC_AUTH_PASSWORD']
    )


class CourseCreationException(Exception):
    """Raised when the creation of a course fails"""
    pass


class CourseSeeder(object):
    """
    Class for course creation actions

    Will create a course in the provided studio link and the import a tarfile
    for a very basic course structure.
    """
    def __init__(self, studio_url):
        self.studio_url = studio_url
        self.sess = requests.Session()
        if BASIC_AUTH_CREDENTIALS is not None:
            self.sess.auth = BASIC_AUTH_CREDENTIALS

    def _headers(self, url):
        """
        Get headers with given url
        """
        try:
            response = self.sess.get(url)
            csrf = response.cookies['csrftoken']
            return {
                'X-CSRFToken': csrf,
                'Referer': url,
                'content-type': 'application/json',
                'Accept': 'application/json'
            }

        except Exception as error:  # pylint: disable=W0703
            print "Error when retrieving csrf token.", error

    def login_to_studio(self, email, password):
        """
        Use given credentials to login to studio.

        Attributes:
            email (str): Login email
            password (str): Login password
        """
        signin_url = '{}/signin'.format(self.studio_url)
        login_url = '{}/login_post'.format(self.studio_url)
        print 'Logging in to {}'.format(self.studio_url)

        response = self.sess.post(
            login_url,
            data={
                'email': email,
                'password': password,
                'honor_code': 'true'
            },
            headers=self._headers(signin_url)).json()

        if not response['success']:
            raise Exception(str(response))

        print 'Login successful'

    def create_course(self, course_data):
        """
        Creates a course with given data and then returns the course key

        Arguments:
            course_data (dict): Org, course, run, and display_name

        Returns:
            course_id for successful course creation

        Raises:
            CourseCreationException when a course creation failure
        """
        print "Creating course with this course data: {}".format(course_data)
        url = '{}/course/'.format(self.studio_url)
        response = self.sess.post(url, json=course_data, headers=self._headers(self.studio_url))

        if response.status_code != 200:
            raise CourseCreationException("{}: {}".format(response.status_code, response.content))
        elif "course_key" not in response.content:
            raise CourseCreationException(response.content[:100])

        return json.loads(response.content)["course_key"]

    def import_tarfile(self, course_id, tarfile):
        url = '{}/import/{}'.format(self.studio_url, course_id)
        print 'Importing {} to {} from {}'.format(course_id, url, tarfile)
        print 'Upload may take a while depending on size of the course'

        headers = self._headers(url)
        headers.pop("content-type")

        with open(tarfile, 'rb') as upload:
            filename = os.path.basename(tarfile)
            upload.seek(0, 2)
            end = upload.tell()
            upload.seek(0, 0)

            while 1:
                start = upload.tell()
                data = upload.read(2 * 10**7)
                if not data:
                    break
                stop = upload.tell() - 1
                files = [
                    ('course-data', (filename, data, 'application/x-gzip'))
                ]
                headers['Content-Range'] = crange = '%d-%d/%d'\
                                                    % (start, stop, end)
                response = self.sess.post(url, files=files, headers=headers)
            # now check import status
            import_status_url = '{}/import_status/{}/{}'.format(
                self.studio_url, course_id, filename)
            status = 0
            while status != 4:
                status = self.sess.get(import_status_url).json()['ImportStatus']
                time.sleep(3)
            print 'Uploaded!'
