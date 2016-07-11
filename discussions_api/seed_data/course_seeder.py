import json
import os
import time

from seeder import Seeder


class CourseCreationException(Exception):
    """Raised when the creation of a course fails"""
    pass


class CourseSeeder(Seeder):
    """
    Class for course creation actions

    Will create a course in the provided studio link and the import a tarfile
    for a very basic course structure.
    """
    def __init__(self, studio_url):
        super(CourseSeeder, self).__init__(studio_url=studio_url)

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
        response = self.sess.post(url, json=course_data, headers=self.get_post_headers(self.studio_url))

        if response.status_code != 200:
            raise CourseCreationException("{}: {}".format(response.status_code, response.content))
        elif "course_key" not in response.content:
            raise CourseCreationException(response.content[:100])

        return json.loads(response.content)["course_key"]

    def import_tarfile(self, course_id, tarfile):
        url = '{}/import/{}'.format(self.studio_url, course_id)
        print 'Importing {} to {} from {}'.format(course_id, url, tarfile)
        print 'Upload may take a while depending on size of the course'

        headers = self.get_post_headers(url)
        headers.pop("Content-Type")

        with open(os.path.join(os.path.dirname(__file__), tarfile), 'rb') as upload:
            filename = os.path.basename(tarfile)
            upload.seek(0, 2)
            end = upload.tell()
            upload.seek(0, 0)

            while 1:
                start = upload.tell()
                data = upload.read(2 * (10 ** 7))
                if not data:
                    break
                stop = upload.tell() - 1
                files = [
                    ('course-data', (filename, data, 'application/x-gzip'))
                ]
                headers['Content-Range'] = '%d-%d/%d' % (start, stop, end)
                self.sess.post(url, files=files, headers=headers)
            # now check import status
            import_status_url = '{}/import_status/{}/{}'.format(
                self.studio_url, course_id, filename)
            status = 0
            while status != 4:
                status = self.sess.get(import_status_url).json()['ImportStatus']
                time.sleep(3)
            print 'Uploaded!'
