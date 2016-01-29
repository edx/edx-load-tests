import logging

from helpers.auto_auth_tasks import AutoAuthTasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommerceTasks(AutoAuthTasks):
    """Base task class for exercising commerce-related operations on the LMS.

    These tests use the auto_auth endpoint on the LMS to generate unique users. These users
    are replicated on the ecommerce service when the LMS issues requests to it on their behalf.
    """

    def on_start(self):
        """Setup code. Run once, before any tasks are scheduled."""
        pass

    def post(self, *args, **kwargs):
        """Perform a POST."""
        kwargs['headers'] = self.post_headers
        # Bypass SSL certificate verification
        kwargs['verify'] = False

        return self._request('post', *args, **kwargs)

    @property
    def post_headers(self):
        """Boilerplate headers for HTTP POST requests."""
        return {
            'X-CSRFToken': self.client.cookies.get('csrftoken', ''),
            'Referer': self.locust.host,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _request(self, method, path, *args, **kwargs):
        """Single internal helper for setting up requests."""
        logger.debug(path)
        return getattr(self.client, method)(path, *args, **kwargs)
