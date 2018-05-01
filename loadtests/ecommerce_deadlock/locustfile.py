import urllib3
import sys
import os

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from helpers import settings, markers
from locust import HttpLocust, TaskSet
settings.init(
    'ecommerce_deadlock.',  # This is a hack to allow the settings code to find the settings file.
    required_data=['ECOMMERCE_HOST', 'LMS_HOST'],
)
from loadtests.ecommerce_deadlock.tasks.LMS_user_tasks import ManualUserBasketTaskSet, AutoAuthUserBasketTaskSet
from loadtests.ecommerce_deadlock.tasks.ecommerce_user_tasks import EcommerceWorkerBasketTaskSet


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
markers.install_event_markers()


class EcommerceTaskSet(TaskSet):
    tasks = {
        ManualUserBasketTaskSet: 3,
        # AutoAuthUserBasketTaskSet: 1,
        EcommerceWorkerBasketTaskSet: 1
    }


class EcommerceLocust(HttpLocust):
    # Explicitly set host to avoid confusion since we are testing with multiple IDAs
    host = settings.data['LMS_HOST']

    min_wait = 3 * 1750
    max_wait = 5 * 1750
    task_set = EcommerceTaskSet
