"""
Load tests for course import from studio.

By default, this tests loading a relatively small course. I recommend
exporting a large course from edX and using it here.
"""
import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import random
import time

from locust import HttpLocust, TaskSet, task, events

from helpers import settings
settings.init(__name__, required=[
    'CMS_USER_EMAIL',
    'CMS_USER_PASSWORD',
    'TEST_FILE',
    'NUM_PARALLEL_COURSES',
])


class CourseImport(TaskSet):
    "Course import task set -- creates course and imports tarballs."

    def on_start(self):
        "Setup method; log in to studio and create courses."

        self.login()

        for i in xrange(settings.data['NUM_PARALLEL_COURSES']):
            self.create_course(i)

    def login(self):
        "Log in to CMS."

        if settings.data.get('BASIC_AUTH_USER') is not None:
            self.client.auth = (
                settings.data['BASIC_AUTH_USER'],
                settings.data['BASIC_AUTH_PASS'],
            )
        self.client.get("/logout")
        self.client.get("/signin")
        response = self.client.post("/login_post",
                                    data={'email': settings.data['CMS_USER_EMAIL'],
                                          'password': settings.data['CMS_USER_PASSWORD'],
                                          'honor_code': 'true',
                                          'csrfmiddlewaretoken':
                                          self.client.cookies['csrftoken']},
                                    headers={'referer':
                                             '{0}/signin'.format(
                                                 self.client.base_url)})
        if response.status_code != 200:
            raise Exception('Login failed: ' + response.text)

        # FIXME: While running this test, I needed to comment the following
        # line.  My goal is not to debug this test, so I will leave it
        # uncommented. --@TroySankey
        self.client.auth = None

        response = self.client.get("/home/")
        if response.text.find("Currently signed in as:") < 0:
            raise Exception('Login failed.')

    def create_course(self, num):
        """Create a course with run number 'num'

        Arguments:
        num - the rerun id to use.
        """

        self.client.get("/home/")
        response = self.client.post("/course/",
                                    json={"org": "LocustX",
                                          "number": "Soup101",
                                          "display_name":
                                          "Soup is Delicious, etc.",
                                          "run": "X{0:02d}".format(num)},
                                    headers={'referer':
                                             '{0}/home/'.format(
                                                 self.client.base_url),
                                             'accept': 'application/json',
                                             'X-CSRFToken':
                                             self.client.cookies['csrftoken']})
        if response.status_code != 200:
            raise Exception('Course creation failed: ' + response.text)

    def import_course(self, num):
        "Import a course over run number 'num'."

        with open(settings.data['TEST_FILE'], "rb") as test_fp:
            cid = "course-v1:LocustX+Soup101+X{0:02d}".format(num)
            import_url = "/import/{0}".format(cid)
            ifname = "some{0:08d}.tar.gz".format(int(random.random() * 1e8))
            self.client.get(import_url, name="/import")
            start_time = time.time()
            resp = self.client.post(import_url,
                                    name="/import",
                                    headers={'referer':
                                             "{0}{1}".format(
                                                 self.client.base_url,
                                                 import_url),
                                             'accept': 'application/json',
                                             'X-CSRFToken':
                                             self.client.cookies['csrftoken']},
                                    files={'course-data':
                                           (ifname,
                                            test_fp,
                                            "application/x-compressed")})
            if resp.status_code != 200:
                raise Exception('Course import failed.')
            for _ in xrange(100):
                resp = self.client.get("/import_status/{0}/{1}".format(cid,
                                                                       ifname),
                                       name="/import_status/")
                if resp.text.find("4") >= 0 or resp.text.find("0") >= 0:
                    break
                time.sleep(0.1)
            if resp.text.find("4") >= 0:
                events.request_success.fire(request_type="http",
                                            name="course_import",
                                            response_time=(time.time() - start_time) * 1000,
                                            response_length=0)
            else:
                events.request_failure.fire(request_type="http",
                                            name="course_import",
                                            response_time=(time.time() - start_time) * 1000)

    @task
    def import_random_course(self):
        "Import a course, overwriting a random course."

        num = random.randrange(settings.data['NUM_PARALLEL_COURSES'])
        self.import_course(num)


class WebsiteUser(HttpLocust):
    "Locust user class."

    task_set = CourseImport
    min_wait = 10
    max_wait = 50
