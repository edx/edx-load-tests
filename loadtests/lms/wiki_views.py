from random import randint
from locust import task
from helpers.interrupt_after import interrupt_after

from base import LmsTasks

from helpers import settings


class WikiViewTask(LmsTasks):
    """
    A very simple task that will hit one of ~13k pre-seeded wiki articles
    I've created for the demo course on my sandbox.
    """

    @task
    @interrupt_after
    def view_article(self):
        """
        Request one of the articles known to exist.

        Articles were seeded with an incrementing numerical slug, so random access is easy.
        """
        path = 'wiki/{}/'.format(randint(settings.data['LOW_WIKI_SLUG'], settings.data['HIGH_WIKI_SLUG']))
        self.get(path, name='wiki:article')
