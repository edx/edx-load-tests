"""
Load tests for the courseware student module.
"""
# from gevent import monkey
# monkey.patch_all()


# import pymysql
# Monkeypatch MySQLdb to a gevent-compatible library
# pymysql.install_as_MySQLdb()

import bisect
import csv
import logging
import numpy
import os
import random
import string
import sys
import time
import types

from locust import Locust, TaskSet, task, events, web
from locust.exception import LocustError

from warnings import filterwarnings
import MySQLdb as Database

from helpers.raw_logs import RawLogger
from helpers import datadog_reporting

os.environ["DJANGO_SETTINGS_MODULE"] = "csm.locustsettings"
# Load settings here to trigger edx-platform sys.path manipulations
from django.conf import settings  # noqa
settings.INSTALLED_APPS

import dogstats_wrapper as dog_stats_api
import courseware.user_state_client as user_state_client  # noqa
from student.tests.factories import UserFactory  # noqa
from opaque_keys.edx.locator import BlockUsageLocator, CourseLocator  # noqa

LOG = logging.getLogger(__file__)
RANDOM_CHARACTERS = [random.choice(string.ascii_letters + string.digits) for __ in xrange(1000)]

from django.db import transaction, connection  # noqa

with open(os.path.join(os.path.dirname(__file__), 'csm-sizes.csv')) as sizes:
    reader = csv.reader(sizes)
    reader.next()  # Drop the header row
    CSM_SIZES = []
    CSM_COUNT = 0
    for count, length in reader:
        CSM_COUNT += int(count)
        CSM_SIZES.append((CSM_COUNT, int(length)))


# TODO: This won't work well if we want to import this file
# from some other test. For that to work, locust would need
# a way to signal which file is the primary test file.
REQUEST_LOGGER = RawLogger()

datadog_reporting.setup()


class UserStateClient(object):
    '''A wrapper class around DjangoXBlockUserStateClient. This does
    two things that the original class does not do:
    * It reports statistics meaningfully to Locust.
    * It provides convenience methods for load-testing (at the moment,
      this is only a method "username" which returns the username
      associated with the client instance).
    '''
    API_DATADOG_SAMPLE_RATE = 0.01

    def __init__(self, user):
        '''Constructor. The argument 'user' is passed to the
        DjangoXBlockUserStateClient constructor.'''
        self._client = user_state_client.DjangoXBlockUserStateClient(user)

    @property
    def username(self):
        "Convenience method. Returns the username associated with the client."
        return self._client.user.username

    def _ddog_histogram(self, evt_time, evt_name, value):
        """
        DataDog histogram method.
        """
        dog_stats_api.histogram(
            'DjangoXBlockUserStateClient.{}'.format(evt_name),
            value,
            timestamp=evt_time,
            sample_rate=self.API_DATADOG_SAMPLE_RATE,
        )

    def __getattr__(self, name):
        "Wraps around client methods and reports stats to locust."
        func = getattr(self._client, name)

        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                if isinstance(result, types.GeneratorType):
                    # To make a generator actually be called, iterate over all the results.
                    result = list(result)
            except Exception as e:
                end_time = time.time()
                total_time = (end_time - start_time) * 1000
                LOG.warning("Request Failed", exc_info=True)
                events.request_failure.fire(
                    request_type="DjangoXBlockUserStateClient",
                    name=name,
                    response_time=total_time,
                    start_time=start_time,
                    end_time=end_time,
                    exception=e
                )
                self._ddog_histogram(end_time, '{}.failure_response_time'.format(name), total_time)
            else:
                end_time = time.time()
                total_time = (end_time - start_time) * 1000
                events.request_success.fire(
                    request_type="DjangoXBlockUserStateClient",
                    name=name,
                    response_time=total_time,
                    start_time=start_time,
                    end_time=time.time(),
                    response_length=0
                )
                self._ddog_histogram(end_time, '{}.success_response_time'.format(name), total_time)
                return result
        return wrapper


class CSMLoadModel(TaskSet):
    """
    Generate load for courseware.StudentModule using the model defined here:
    https://openedx.atlassian.net/wiki/display/PLAT/CSM+Loadtest+Request+Modelling
    """

    def __init__(self, *args, **kwargs):
        super(CSMLoadModel, self).__init__(*args, **kwargs)
        self.course_key = CourseLocator('org', 'course', 'run')
        self.usages_with_data = set()

    def _gen_field_count(self):
        # Instead of picking from a distribution that will continually increase the number of fields per block,
        # just make all blocks have three fields for now.
        return 3

    def _gen_block_type(self):
        return random.choice(['problem', 'html', 'sequence', 'vertical'])

    def _gen_block_size(self):
        i = bisect.bisect(CSM_SIZES, (random.randint(0, CSM_COUNT), 0))
        return CSM_SIZES[i][1]

    def _gen_block_data(self):
        target_serialized_size = self._gen_block_size()
        num_fields = self._gen_field_count()

        if target_serialized_size == 2:
            return {}
        else:
            # A serialized field looks like: `"key": "value",`.
            # We'll use a standard set of single characters for keys (so that
            # our data overlaps). So, we need 1 char for the key, 6 for the syntax,
            # and the rest goes to the value.
            data_per_field = max(target_serialized_size // num_fields - 6, 0)
            return {
                str(field): (RANDOM_CHARACTERS * (data_per_field // 1000 + 1))[:data_per_field]
                for field in range(num_fields)
            }

    def _gen_num_blocks(self):
        # Limit the Pareto distribution to remove large numbers that happen over time.
        return min(int(numpy.random.pareto(a=2.21) + 1), 1000)

    def _gen_usage_key(self):
        return BlockUsageLocator(
            self.course_key,
            self._gen_block_type(),
            # We've seen at most 1000 blocks requested in a course, so we'll
            # generate at most that many different indexes.
            str(numpy.random.randint(0, 1000)),
        )

    @task(1)
    @transaction.commit_manually
    def get_many(self):
        block_count = self._gen_num_blocks()
        if block_count > len(self.usages_with_data):
            # Create the number of blocks up to block_count.
            for __ in xrange(block_count - len(self.usages_with_data)):
                self.set_many()
        else:
            # TODO: This doesn't accurately represent queries which would retrieve
            # data from StudentModules with no state, or usages with no StudentModules
            self.client.get_many(
                self.client.username,
                random.sample(self.usages_with_data, block_count)
            )
        transaction.commit()
        connection.close()

    @task(1)
    @transaction.commit_manually
    def set_many(self):
        usage_key = self._gen_usage_key()
        self.client.get_many(self.client.username, [usage_key])
        self.client.set_many(self.client.username, {usage_key: self._gen_block_data()})
        self.usages_with_data.add(usage_key)
        transaction.commit()
        connection.close()


class UserStateClientClient(Locust):
    "Locust class for the User State Client."

    task_set = CSMLoadModel
    min_wait = 1
    max_wait = 1

    def __init__(self):
        '''Constructor. DATABASE environment variables must be set
        (via locustsetting.py) prior to constructing this object.'''
        super(UserStateClientClient, self).__init__()

        # Without this, the greenlets will halt for database warnings
        filterwarnings('ignore', category=Database.Warning)

        self.client = UserStateClient(user=UserFactory.create())


# Help the template loader find our template.
web.app.jinja_loader.searchpath.append(
    os.path.join(os.path.dirname(__file__), 'templates'))


@web.app.route("/set_params", methods=['GET', 'POST'])
def set_params():
    '''Convenience method; creates a page (via flask) for setting
    database parameters when locust's web interface is enabled.'''
    if web.request.method == 'POST':
        if len(web.request.form['PASSWORD']) > 0:
            settings.DATABASES['default']['PASSWORD'] \
                = web.request.form['PASSWORD']
        for key in ['USER', 'PORT', 'NAME', 'HOST']:
            settings.DATABASES['default'][key] = web.request.form[key]
    return web.render_template('set_params.html',
                               **settings.DATABASES['default'])
