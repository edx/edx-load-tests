import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from locust import HttpLocust, TaskSet

from baskets import BasketsTasks
from payment import CybersourcePaymentTasks
from helpers import settings


settings.init(__name__, required=['ecommerce', 'jwt'])


class EcommerceTest(TaskSet):
    """Load test exercising ecommerce-related operations on the LMS and Otto.

    Execution probabilities are derived from a conservative estimate from
    marketing placing the percentage of paid enrollments at 2% of all
    enrollments.
    """
    tasks = {
        BasketsTasks: 50,
        CybersourcePaymentTasks: 1,
    }


class EcommerceUser(HttpLocust):
    """Representation of an HTTP "user".

    Defines how long a simulated user should wait between executing tasks, as
    well as which TaskSet class should define the user's behavior.
    """
    task_set = EcommerceTest
    min_wait = 3 * 1000
    max_wait = 5 * 1000
