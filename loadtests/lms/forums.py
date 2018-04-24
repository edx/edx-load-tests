from collections import deque
import logging
import os
import random
import string

from lazy import lazy
from base import LmsTasks
from locust import task

from helpers import settings

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

DICTIONARY_FILENAME = 'words.txt'
_dictionary_words = []


def _random_word_from_dictionary():
    """
    Get a random word from the dictionary file.
    """
    global _dictionary_words
    dictionary_path = os.path.join(os.path.dirname(__file__), DICTIONARY_FILENAME)
    # cache the entire dictionary in memory
    if not _dictionary_words:
        _dictionary_words = open(dictionary_path).read().splitlines()

    return random.choice(_dictionary_words)


def _dummy_text(minlen, maxlen):
    """
    Helper function to generate dummy text where needed in forums submissions.
    """
    desired_length = random.randrange(minlen, maxlen)
    buf = ''
    # We'll shoot for desired_length, but may end up overshooting.  It doesn't
    # really matter.
    while len(buf) < desired_length + 1:
        buf += _random_word_from_dictionary()
        buf += ' '
    buf = buf[0:-1]  # cut off trailing space
    buf = buf[0:maxlen]  # truncate
    return buf


class BaseForumsTasks(LmsTasks):
    """
    Base class for Forums (LMS) TaskSets.

    This class reads the following optional settings:

    * LARGE_TOPIC_ID: Topic id for the large thread.
    * LARGE_THREAD_ID: Thread id for the large thread.

    See subclasses for usage.

    """

    # class variables used to share across locust users.
    ###
    # track the large thread tuple (topic_id, thread_id).
    _large_thread = None
    # cache of IDs for all topics in the course
    _all_topic_ids = None

    def random_topic_id(self):
        """
        randomly choose the topic_id (aka discussion_id or commentable_id)
        """
        return random.choice(self.topic_ids())

    def topic_ids(self):
        # use Discussion API to load topics
        if not BaseForumsTasks._all_topic_ids:
            url = '/api/discussion/v1/course_topics/{}/'.format(self.course_key)
            response = self.client.get(url, verify=False, name='forums:get_topics')
            response_json = response.json()

            BaseForumsTasks._all_topic_ids = []
            for topic in response_json['non_courseware_topics']:
                BaseForumsTasks._all_topic_ids.append(topic['id'])
            for topic in response_json['courseware_topics']:
                for child in topic['children']:
                    BaseForumsTasks._all_topic_ids.append(child['id'])

        return BaseForumsTasks._all_topic_ids

    @lazy
    def large_topic_id(self):
        """
        The topic id of the large thread.
        """
        if BaseForumsTasks._large_thread:
            return BaseForumsTasks._large_thread[0]
        else:
            try:
                return self._get_course_setting('large_topic_id')
            except KeyError:
                return None

    @lazy
    def large_thread_id(self):
        """
        The thread id of the large thread.
        """
        if BaseForumsTasks._large_thread:
            return BaseForumsTasks._large_thread[1]
        else:
            try:
                return self._get_course_setting('large_thread_id')
            except KeyError:
                return None

    def create_thread(self, topic_id, name):
        """
        Create a new thread in the topic_id.

        Returns:
            Tuple: (topic_id, thread_id)
        """
        thread_data = {
            'body': _dummy_text(100, 2000),  # NB size range not based on actual data.
            'title': _dummy_text(20, 100),  # NB size range not based on actual data.
            'thread_type': random.choice(('discussion', 'question')),
            'anonymous_to_peers': 'false',
            'anonymous': 'false',
            'auto_subscribe': 'true',
        }

        response = self.post(
            'discussion/{}/threads/create'.format(topic_id),
            data=thread_data,
            name=name,
        )

        thread_id = response.json()['id']
        return (topic_id, thread_id)

    def update_thread(self, thread_id):
        """
        Edit (update) a given existing thread.

        This will modify both the thread body and thread title.

        Arguments:
            thread_id: ID of the thread which will be updated
        """
        thread_data = {
            'body': _dummy_text(100, 2000),  # NB size range not based on actual data.
            'title': _dummy_text(20, 100),  # NB size range not based on actual data.
        }

        self.post(
            'discussion/threads/{}/update'.format(thread_id),
            data=thread_data,
            name='forums:update_thread',
        )

    def large_thread(self):
        """
        Read the large thread.
        """
        if not self.large_topic_id or not self.large_thread_id:
            return

        skip_limit = random.choice((('0', '25'), ('25', '100'), ('125', '100')))

        self.get(
            'discussion/forum/{}/threads/{}'.format(self.large_topic_id, self.large_thread_id),
            params={
                'resp_skip': skip_limit[0],
                'resp_limit': skip_limit[1],
            },
            name='forums:large_thread',
        )

    def create_response(self, thread_id):
        """
        Post a response to an existing thread.
        """
        thread_data = {
            'body': _dummy_text(100, 2000),  # NB size range not based on actual data.
        }
        response = self.post(
            'discussion/threads/{}/reply'.format(thread_id),
            data=thread_data,
            name='forums:create_response',
        )

        return response.json()['id']

    def create_comment(self, response_id):
        """
        Post a response to an existing thread.
        """
        thread_data = {
            'body': _dummy_text(100, 2000),  # NB size range not based on actual data.
        }
        self.post(
            'discussion/comments/{}/reply'.format(response_id),
            data=thread_data,
            name='forums:create_comment',
        )


class ForumsTasks(BaseForumsTasks):
    """
    Forums (LMS) TaskSet.

    This class uses the following optional settings:

    * LARGE_TOPIC_ID: Topic id for the large thread.  If absent, all reads
        will be against normal sized threads.
    * LARGE_THREAD_ID: Thread id for the large thread.  If absent, all reads
        will be against normal sized threads.

    """

    # class variable used to share across locust users.
    # keep track of thread ids created during a test, so they can be used to formulate read requests and replies.
    # a deque is used instead of a list in order to enforce maximum length.
    _thread_ids = deque(maxlen=1000)

    """
    Traffic distribution must come from LMS/discussions calls, not from comment
    service calls directly, in case the LMS calls make non-obvious comment
    service calls.

    For more up to date details on choosing weightings, see:
    https://openedx.atlassian.net/wiki/display/TNL/Forums+Performance

    """
    @task(10)
    def forum_form_discussion(self):
        """
        Visit the discussion tab.
        """
        self.get('discussion/forum', name="forums:forum_form_discussion")

    @task(4)
    def select_topic(self):
        """
        Load a randomly-selected topic from the discussion tab sidebar.
        """
        self.get(
            'discussion/forum/',
            params={
                'commentable_ids': self.random_topic_id(),
                'page': '1',
            },
            name='forums:select_topic',
        )

    @task(4)
    def search_text(self):
        """
        Search for some random words.

        This should hit Elasticsearch.
        """
        self.get(
            'discussion/forum/search',
            params={
                'text': _random_word_from_dictionary(),
            },
            name='forums:search_text',
        )

    @task(10)
    def inline_discussion(self):
        """
        Load a randomly-selected inline discussion.
        """
        self.get(
            'discussion/forum/{}/inline'.format(self.random_topic_id()),
            params={'page': '1'},
            name='forums:inline_discussion',
        )

    @task(4)
    def create_thread(self):
        """
        create a new thread in a randomly-selected topic
        """
        thread = super(ForumsTasks, self).create_thread(self.random_topic_id(), name='forums:create_thread')
        ForumsTasks._thread_ids.append(thread)
        self.locust._my_thread_ids.append(thread)

    @task(1)
    def update_thread(self):
        """
        Edit (update) an existing thread.

        The thread to update is randomly-selected from the cache of IDs for
        threads which this locust user has created.  LMS users cannot edit each
        others' threads.
        """
        if not self.locust._my_thread_ids:
            return
        discussion_id, thread_id = random.choice(self.locust._my_thread_ids)
        super(ForumsTasks, self).update_thread(thread_id)

    @task(36)
    def single_thread(self):
        """
        Read a specific thread.
        """
        if not ForumsTasks._thread_ids:
            return
        discussion_id, thread_id = random.choice(ForumsTasks._thread_ids)

        self.get(
            'discussion/forum/{}/threads/{}'.format(discussion_id, thread_id),
            params={
                'resp_skip': '0',
                'resp_limit': '25',
            },
            name='forums:single_thread',
        )

    @task(23)
    def large_thread(self):
        """
        Read the large thread.
        """
        if self.large_topic_id and self.large_thread_id:
            super(ForumsTasks, self).large_thread()

        else:
            # Fall back to regular read if not configured for long thread test
            self.single_thread()

    @task(4)
    def create_response(self):
        """
        Post a response to an existing thread.
        """
        if not ForumsTasks._thread_ids:
            # Skip if we haven't created any threads yet during this test.
            return
        discussion_id, thread_id = random.choice(ForumsTasks._thread_ids)

        super(ForumsTasks, self).create_response(thread_id)

    @task(1)
    def user_profile(self):
        """
        Request the user profile endpoint.
        """
        self.get(
            'discussion/forum/users/{}'.format(self.locust._user_id),
            name='forums:get_user_profile',
        )

    @task(1)
    def followed_threads(self):
        """
        Request the followed threads endpoint.
        """
        self.get(
            'discussion/forum/users/{}/followed'.format(self.locust._user_id),
            headers={"X-Requested-With": "XMLHttpRequest"},  # non-ajax requests don't work here.
            name='forums:followed_threads',
        )

    @task(11)
    def stop(self):
        """
        Switch to another TaskSet.
        """
        self.interrupt()

    def on_start(self):
        """
        This on_start method performs the following actions:
        1. Logs in and enrolls (using super)
        2. Loads the course's topic ids
        """
        super(ForumsTasks, self).on_start()
        self.topic_ids()
        if getattr(self.locust, '_my_thread_ids', None) is None:
            self.locust._my_thread_ids = []


class SeedForumsTasks(BaseForumsTasks):
    """
    Seed large thread for Forums (LMS) TaskSet.

    This class supports environment-based configuration to override default
    values for the following:

    * LARGE_TOPIC_ID: Topic id for the large thread to be extended.  If blank,
        a new thread will be created and the topic id will be printed.
    * LARGE_THREAD_ID: Thread id for the large thread to be extended.  If blank,
        a new thread will be created and the thread id will be printed.

    """

    # class variable used to share across locust users.
    # track responses on the large thread.
    _large_thread_response_ids = deque(maxlen=100)

    @task(10)
    def create_response(self):
        """
        Post a response to an existing thread.
        """
        if SeedForumsTasks._large_thread is None:
            return

        discussion_id, thread_id = SeedForumsTasks._large_thread

        response_id = super(SeedForumsTasks, self).create_response(thread_id)

        # clump comments on a few responses
        if (
            not SeedForumsTasks._large_thread_response_ids or
            random.randint(1, len(SeedForumsTasks._large_thread_response_ids)) <= 1
        ):
            SeedForumsTasks._large_thread_response_ids.append(response_id)

    @task(1)
    def create_comment(self):
        """
        Post a response to an existing thread.
        """
        if not SeedForumsTasks._large_thread_response_ids:
            return
        response_id = random.choice(SeedForumsTasks._large_thread_response_ids)

        super(SeedForumsTasks, self).create_comment(response_id)

    def on_start(self):
        """
        This on_start method performs the following actions:
        1. Logs in and enrolls (using super)
        2. Loads the course's topic ids
        3. Creates a thread (seed for large thread)
        4. Outputs log messages with details for running other tasks
        """
        super(SeedForumsTasks, self).on_start()
        if SeedForumsTasks._large_thread is None:
            # Are we extending an existing long thread?
            if self.large_topic_id and self.large_thread_id:
                SeedForumsTasks._large_thread = (self.large_topic_id, self.large_thread_id)

            # Otherwise, create a new thread.
            else:
                SeedForumsTasks._large_thread = self.create_thread(self.random_topic_id(), name='forums:create_large_thread')

            LOGGER.info('To run ForumsTasks with this large thread, use:\nLARGE_TOPIC_ID={} LARGE_THREAD_ID={}'.format(
                SeedForumsTasks._large_thread[0], SeedForumsTasks._large_thread[1]
            ))
