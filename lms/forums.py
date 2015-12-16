from collections import deque
import random
import string

from locust import task

from lms import LmsTasks


# keep track of thread ids created during a test, so they can be used to formulate read requests and replies.
# a deque is used instead of a list in order to enforce maximum length.
_thread_ids = deque(maxlen=1000)
_dummy_chars = string.lowercase + '      '


def _dummy_text(minlen, maxlen):
    """
    Naive helper function to generate dummy text where needed in forums submissions.
    """

    return ''.join(random.choice(_dummy_chars) for _ in xrange(minlen, random.randrange(minlen + 1, maxlen)))


class ForumsTasks(LmsTasks):
    """
    Simulate traffic for endpoints in lms.djangoapps.django_comment_client.base and .views

    Traffic Distribution on courses.edx.org (last 7d as of 2014-02-24):

    /django_comment_client.base.views:create_comment            17205     1.73%
    /django_comment_client.base.views:create_sub_comment        8489      0.85%
    /django_comment_client.base.views:create_thread             31984     3.22%
    /django_comment_client.base.views:delete_comment            434       0.04%
    /django_comment_client.base.views:delete_thread             368       0.04%
    /django_comment_client.base.views:endorse_comment           1032      0.10%
    /django_comment_client.base.views:flag_abuse_for_comment    69        0.01%
    /django_comment_client.base.views:flag_abuse_for_thread     62        0.01%
    /django_comment_client.base.views:follow_thread             2895      0.29%
    /django_comment_client.base.views:openclose_thread          27        0.00%
    /django_comment_client.base.views:pin_thread                177       0.02%
    /django_comment_client.base.views:un_flag_abuse_for_comment 35        0.00%
    /django_comment_client.base.views:un_flag_abuse_for_thread  36        0.00%
    /django_comment_client.base.views:un_pin_thread             70        0.01%
    /django_comment_client.base.views:undo_vote_for_comment     285       0.03%
    /django_comment_client.base.views:undo_vote_for_thread      490       0.05%
    /django_comment_client.base.views:unfollow_thread           567       0.06%
    /django_comment_client.base.views:update_comment            2483      0.25%
    /django_comment_client.base.views:update_thread             1891      0.19%
    /django_comment_client.base.views:upload                    1051      0.11%
    /django_comment_client.base.views:users                     13678     1.38%
    /django_comment_client.base.views:vote_for_comment          4691      0.47%
    /django_comment_client.base.views:vote_for_thread           7012      0.71%
    /django_comment_client.forum.views:followed_threads         7910      0.80%
    /django_comment_client.forum.views:forum_form_discussion    184475    18.55%
    /django_comment_client.forum.views:inline_discussion        150204    15.11%
    /django_comment_client.forum.views:single_thread            547876    55.10%
    /django_comment_client.forum.views:user_profile             8765      0.88%
    """

    @task(19)
    def forum_form_discussion(self):
        """
        Visit the discussion tab.
        """
        self.get('discussion/forum', name="forums:forum_form_discussion")

    @task(5)
    def search_topic(self):
        """
        Load a randomly-selected topic from the discussion tab sidebar.
        Uses ES, but not actually a search from the user perspective.
        """
        self.get(
            'discussion/forum/search',
            params={
                'commentable_ids': self.course_data.discussion_id,
                'page': '1',
            },
            name='forums:search_topic',
        )

    @task(15)
    def inline_discussion(self):
        """
        Load a randomly-selected inline discussion.
        """
        self.get(
            'discussion/forum/{}/inline'.format(self.course_data.discussion_id),
            params={'page': '1'},
            name='forums:inline_discussion',
        )

    @task(4)
    def create_thread(self):
        """
        create a new thread in a randomly-selected topic
        """
        thread_data = {
            'body': _dummy_text(100, 2000),  # NB size range not based on actual data.
            'title': _dummy_text(20, 100),  # NB size range not based on actual data.
            'thread_type': random.choice(('discussion', 'question')),
            'anonymous_to_peers': 'false',
            'anonymous': 'false',
            'auto_subscribe': 'true',
        }
        discussion_id = self.course_data.discussion_id

        response = self.post(
            'discussion/{}/threads/create'.format(discussion_id),
            data=thread_data,
            name='forums:create_thread',
        )

        _thread_ids.append((discussion_id, response.json()['id']))

    @task(55)
    def single_thread(self):
        """
        Read a specific thread.
        """
        if not _thread_ids:
            return
        discussion_id, thread_id = random.choice(_thread_ids)

        self.get(
            'discussion/forum/{}/threads/{}'.format(discussion_id, thread_id),
            params={
                'resp_skip': '0',
                'resp_limit': '25',
            },
            name='forums:single_thread',
        )

    @task(3)
    def create_comment(self):
        """
        Post a response to an existing thread.
        """
        if not _thread_ids:
            # Skip if we haven't created any threads yet during this test.
            return
        discussion_id, thread_id = random.choice(_thread_ids)

        thread_data = {
            'body': _dummy_text(100, 2000),  # NB size range not based on actual data.
        }
        self.post(
            'discussion/threads/{}/reply'.format(thread_id),
            data=thread_data,
            name='forums:create_comment',
        )

    @task(1)
    def user_profile(self):
        """
        Request the user profile endpoint.
        """
        self.get(
            'discussion/forum/users/{}'.format(self._user_id),
            name='forums:get_user_profile',
        )

    @task(1)
    def followed_threads(self):
        """
        Request the followed threads endpoint.
        """
        self.get(
            'discussion/forum/users/{}/followed'.format(self._user_id),
            headers={"X-Requested-With": "XMLHttpRequest"},  # non-ajax requests don't work here.
            name='forums:followed_threads',
        )
