import json

from locust import HttpLocust, task, TaskSet
from locust.clients import HttpSession

from course_discovery import config
from helpers.api import LocustEdxRestApiClient


class CourseDiscoveryTaskSet(TaskSet):
    CATALOG_ID = 1

    @task(20)
    def get_catalog_courses(self):
        """ Retrieve all courses associated with a catalog. """
        self.client.catalogs(self.CATALOG_ID).courses.get()

    @task(1)
    def get_catalog(self):
        """ Retrieve catalog details. """
        self.client.catalogs(self.CATALOG_ID).get()

    @task(1)
    def list_catalogs(self):
        """ List all catalogs. """
        self.client.catalogs.get()

    @task(1)
    def list_courses(self):
        """ List the full set of courses. """
        self.client.courses.get()

    @task(10)
    def list_courses_with_query(self):
        """ Query the courses. """
        query = {
            'query': {
                'query_string': {
                    'query': 'org:(MITx OR HarvardX)'
                }
            }
        }
        self.client.courses.get(q=json.dumps(query))


class CourseDiscoveryApiLocust(HttpLocust):
    USERNAME_MAX_LENGTH = 30
    USERNAME_PREFIX = 'load-test-'

    task_set = CourseDiscoveryTaskSet

    def __init__(self):
        super(CourseDiscoveryApiLocust, self).__init__()
        self.client = LocustEdxRestApiClient(
            config.COURSE_DISCOVERY_API_URL,
            session=HttpSession(base_url=self.host)
        )
