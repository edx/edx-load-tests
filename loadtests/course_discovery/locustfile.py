import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import random

from locust import HttpLocust, task, TaskSet
from locust.clients import HttpSession

from helpers import settings
from helpers.api import LocustEdxRestApiClient


settings.init(__name__, required=['oauth', 'programs'])


class SelfInterruptingTaskSet(TaskSet):
    @task(1)
    def stop(self):
        self.interrupt()


class CatalogTaskSet(SelfInterruptingTaskSet):
    catalog_id = 1

    @task(20)
    def get_catalog_courses(self):
        """Retrieve all courses associated with a catalog."""
        self.client.catalogs(self.catalog_id).courses.get()

    @task(10)
    def list_courses_with_query(self):
        """Query the courses."""
        self.client.courses.get(q='organizations:(MITx OR HarvardX)')

    @task(1)
    def get_catalog(self):
        """Retrieve catalog details."""
        self.client.catalogs(self.catalog_id).get()

    @task(1)
    def list_catalogs(self):
        """List all catalogs."""
        self.client.catalogs.get()

    @task(1)
    def list_courses(self):
        """List the full set of courses."""
        self.client.courses.get()


class SearchTaskSet(SelfInterruptingTaskSet):
    queries = ['math', 'biology', 'history']
    facets = ['subjects_exact:Medicine', 'organizations_exact:HarvardX: Harvard University', 'level_type_exact:Intermediate']
    query_facets = ['availability_archived', 'availability_current', 'availability_upcoming']

    @task(10)
    def search_query(self):
        """Search all content types with the given query."""
        query = random.choice(self.queries)
        self.client.search.all.facets.get(q=query)

    @task(5)
    def search_select_facet(self):
        """Filter content types using a facet."""
        facet = random.choice(self.facets)
        self.client.search.all.facets.get(selected_facets=facet)

    @task(1)
    def search_select_query_facet(self):
        """Filter content types using a query (computed) facet."""
        query_facet = random.choice(self.query_facets)
        self.client.search.all.facets.get(selected_query_facets=query_facet)


class ProgramTaskSet(SelfInterruptingTaskSet):
    @task(1)
    def list_marketable_programs(self):
        """List the full set of marketable programs."""
        self.client.programs.get(marketable=1)

    @task(5)
    def filter_marketable_programs(self):
        """Filter the set of marketable programs."""
        program_types = settings.data['programs']['types']
        program_type = random.choice(program_types)
        self.client.programs.get(marketable=1, type=program_type)

    @task(1)
    def get_single_program(self):
        """Get a single program."""
        program_uuids = settings.data['programs']['uuids']
        program_uuid = random.choice(program_uuids)
        self.client.programs(program_uuid).get()


class CourseDiscoveryTaskSet(TaskSet):
    tasks = {
        CatalogTaskSet: 1,
        ProgramTaskSet: 5,
        SearchTaskSet: 10,
    }


class CourseDiscoveryLocust(HttpLocust):
    """Representation of a user.

    Locusts are hatched and used to attack the system being load tested. This class
    defines which TaskSet class should control each locust's behavior.
    """
    min_wait = 3 * 1000
    max_wait = 5 * 1000
    task_set = CourseDiscoveryTaskSet

    def __init__(self):
        super(CourseDiscoveryLocust, self).__init__()

        access_token_endpoint = '{}/oauth2/access_token'.format(
            settings.data['oauth']['provider_url'].strip('/')
        )

        access_token, __ = LocustEdxRestApiClient.get_oauth_access_token(
            access_token_endpoint,
            settings.data['oauth']['client_id'],
            settings.data['oauth']['client_secret'],
        )

        api_url = '{}/api/v1/'.format(self.host.strip('/'))

        self.client = LocustEdxRestApiClient(
            api_url,
            session=HttpSession(base_url=self.host),
            oauth_access_token=access_token
        )
