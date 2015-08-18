"""
Load tests for the courseware student module.
"""

import os
import sys
import time

from locust import Locust, TaskSet, task, events, web
from locust.exception import LocustError

from warnings import filterwarnings
import MySQLdb as Database

sys.path.append(os.path.dirname(__file__))

import locustsettings

os.environ["DJANGO_SETTINGS_MODULE"] = "locustsettings"

import courseware.user_state_client as user_state_client
from student.tests.factories import UserFactory
from opaque_keys.edx.locator import BlockUsageLocator


class QuestionResponse(TaskSet):
    "Respond to a question in the LMS."

    @task
    def set_many(self):
        "set many load test"
        usage = BlockUsageLocator.from_string(
            'block-v1:HarvardX+SPU27x+2015_Q2+type@html+block'
            + '@1a1866accf254461aa2df3e0b4238a5f')
        self.client.set_many(self.client.username,
                             {usage: {"soup": "delicious"}})

    @task
    def get_many(self):
        "get many load test"
        usage = BlockUsageLocator.from_string(
            'block-v1:HarvardX+SPU27x+2015_Q2+type@html+block'
            + '@1a1866accf254461aa2df3e0b4238a5f')
        response = [s for s in self.client.get_many(self.client.username,
                                                    [usage])]


class UserStateClient(object):
    '''A wrapper class around DjangoXBlockUserStateClient. This does
    two things that the original class does not do:
    * It reports statistics meaningfully to Locust.
    * It provides convenience methods for load-testing (at the moment,
      this is only a method "username" which returns the username
      associated with the client instance).
    '''

    def __init__(self, user):
        '''Constructor. The argument 'user' is passed to the
        DjangoXBlockUserStateClient constructor.'''
        self._client = user_state_client.DjangoXBlockUserStateClient(user)

    @property
    def username(self):
        "Convenience method. Returns the username associated with the client."
        return self._client.user.username

    def __getattr__(self, name):
        "Wraps around client methods and reports stats to locust."
        func = getattr(self._client, name)

        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                total_time = int((time.time() - start_time) * 1000)
                events.request_failure.fire(
                    request_type="DjangoXBlockUserStateClient",
                    name=name,
                    response_time=total_time,
                    exception=e)
            else:
                total_time = int((time.time() - start_time) * 1000)
                events.request_success.fire(
                    request_type="DjangoXBlockUserStateClient",
                    name=name,
                    response_time=total_time,
                    response_length=0)
                return result
        return wrapper


class UserStateClientClient(Locust):
    "Locust class for the User State Client."

    task_set = QuestionResponse
    min_wait = 1000
    max_wait = 5000

    def __init__(self):
        '''Constructor. DATABASE environment variables must be set
        (via locustsetting.py) prior to constructing this object.'''
        super(UserStateClientClient, self).__init__()

        if locustsettings.DATABASES['default']['USER'] is None \
                or locustsettings.DATABASES['default']['PASSWORD'] is None \
                or locustsettings.DATABASES['default']['HOST'] is None:
            raise LocustError("You must specify the username, password and "
                              + "host for the database as environment "
                              + "variables DB_USER, DB_PASSWORD and DB_HOST, "
                              + "respectively.")

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
            locustsettings.DATABASES['default']['PASSWORD'] \
                = web.request.form['PASSWORD']
        for key in ['USER', 'PORT', 'NAME', 'HOST']:
            locustsettings.DATABASES['default'][key] = web.request.form[key]
    return web.render_template('set_params.html',
                               **locustsettings.DATABASES['default'])
