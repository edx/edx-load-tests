# pylint: disable=no-member
"""
Parent class of the discussion api tasks.
"""
import json
import logging
import os
import random
import urllib

from helpers import auto_auth_tasks

from tasks import dapi_constants


class UnexpectedResponse(Exception):
    """
    Raised when response is not 200
    """
    pass


class DiscussionsApiTasks(auto_auth_tasks.AutoAuthTasks):
    """
    Parent class of the discussion api tasks.
    """

    def __init__(self, *args, **kwargs):  # pylint: disable=super-on-old-class
        super(DiscussionsApiTasks, self).__init__(*args, **kwargs)
        self.course_id = os.getenv('COURSE_ID')
        self.url_prefix = "/api/discussion/v1"

        if os.getenv('SEEDED_DATA'):
            #with open("discussions_api/" + os.getenv('SEEDED_DATA'), 'r') as seeded_data:
            with open("" + os.getenv('SEEDED_DATA'), 'r') as seeded_data:
                self.thread_id_list = seeded_data.read().splitlines()
        else:
            self.thread_id_list = []

        self.verbose = True if (os.getenv('VERBOSE') == "true") else False
        self.pages = len(self.thread_id_list) / int(dapi_constants.PAGE_SIZE[0])
        if self.pages == 0:
            self.pages = 1
        logging.basicConfig(
            format='%(asctime)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.log = logging.getLogger()

    def random_page_number(self):
        return random.randint(1, self.pages)

    @property
    def _headers(self):
        """Standard header"""
        return {
            'X-CSRFToken': self.client.cookies.get('csrftoken', ''),
            'Referer': self.locust.host,
            'content-type': 'application/json'
        }

    @property
    def _post_headers(self):
        """Headers for POST"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-CSRFToken': self.client.cookies.get('csrftoken', ''),
            'Referer': self.locust.host
        }

    @property
    def _delete_headers(self):
        """Headers for DELETE"""
        return {
            'X-CSRFToken': self.client.cookies.get('csrftoken', ''),
            'Referer': self.locust.host
        }

    def stop(self):
        """
        Supports usage as nested or top-level task set.
        """
        if self.parent != self.locust:
            self.interrupt()

    def wait_then_stop(self):
        """
        Waits, and then stops
        """
        self.wait()
        self.stop()

    def on_start(self):
        """
        For Discussion API tests, user creation is done at the parent task level
        """
        pass

    def verify_response(self, response, url):
        """
        Checks for a 200 response, else prints out the url and partial content

        Raises:
            UnexpectedResponse: raised when we do not get a 200 response.
        """
        if response.status_code != 200:
            self.log.info(url)
            self.log.info(response.status_code)
            raise UnexpectedResponse("{}: {}".format(response.status_code, response.content[0:200]))

    def get_random_thread(self, page=None, page_size=None, prioritize_comments=False, verbose=False):
        """
        Common method for GETing a thread list, and returning the thread

        GET is called significantly more than other endpoints. We use it to get
        thread_id's for other HTTP requests that require a thread info. Since
        different filters and sort key's are randomly used, the 1 page will
        be somewhat random on GET requests, and more random as PATCH, POSTS,
        and DELETES are included.

        Args:
            page (int): If set, will return this page number
            page_size (int): If set, will return this many items per page
            prioritize_comments (Bool): If True, will try to return a thread
                that has comments, namely responses.
            verbose (Bool): Get detailed locust request names

        Returns:
             (dict): The thread
        """
        course_id = "course-v1:edX+DemoX+Demo_Course"
        query_args = {
            #"course_id": urllib.quote_plus(self.course_id),
            "course_id": course_id,
            #"following": random.choice(dapi_constants.FOLLOWING),
            #"view": random.choice(dapi_constants.VIEW),
            "page_size": page_size if page_size else random.choice(dapi_constants.PAGE_SIZE),
            "page": page if page else self.random_page_number(),
            "order_by": "comment_count" if prioritize_comments else random.choice(dapi_constants.ORDER_BY),
            "order_direction": "desc" if prioritize_comments else random.choice(dapi_constants.ORDER_DIRECTION),
        }
        encoded_args = urllib.urlencode(query_args)

        url = "{}/threads/?{}".format(self.url_prefix, encoded_args)
        name = url if verbose else "GET_thread_list"

        response = self.client.get(url=url, verify=False, name=name)

        self.verify_response(response, url)

        if not response.json()["results"]:
            return None

        if prioritize_comments:
            threads_with_comments = [thread for thread in response.json() if thread["comment_count"] > 0]
            if threads_with_comments:
                return random.choice(threads_with_comments)
        return random.choice(response.json()["results"])

    def get_random_comment(self, thread, verbose=False):
        """
        Common method for GETting a comment list, returns the comment

        Similar to _get_thread, GETting a comment happens significantly more
        than other HTTP requests so this method will be used to retrieve
        comment data.

        Args:
            thread (dict): The thread we are getting the comment from
            verbose (Bool): Get detailed locust request names
        """
        query_args = {
            "thread_id": thread["id"],
        }

        # Required for question threads, set to False for discussion
        if thread["type"] == "question":
            #endorsed = "False"  # unless set to false, no comments are returned since endorse is not seeded
            query_args["endorsed"] = "False"
        #else:
        #    endorsed = "None"

        # query_args = {
        #     "thread_id": thread["id"],
        #     "page_size": random.choice(dapi_constants.PAGE_SIZE),
        #     "endorsed": endorsed,
        #     "mark_as_read": random.choice(dapi_constants.MARK_AS_READ),
        #     "page": random.choice(dapi_constants.PAGE),
        # }
        encoded_args = urllib.urlencode(query_args)

        url = "{}/comments/?{}".format(self.url_prefix, encoded_args)

        # Only be useful when running task in isolation with pre-set comment data
        if verbose:
            comment_count, response_count = self.get_comment_and_response_count(thread["id"])
            name = "comment_count={}_response_count={}".format(comment_count, response_count)
        else:
            name = "GET_comment_list"

        response = self.client.get(url, verify=False, name=name)

        self.verify_response(response, url)
        if response.json()["results"]:
            return random.choice(response.json()["results"])
        return None

    def post_thread(self):
        """
        POSTs a thread.

        Returns:
            (dict): The thread.
        """
        body = {
            "course_id": self.course_id,
            "topic_id": "course",
            "type": "discussion",
            "title": "default thread",
            "raw_body": "This is a thread. {}".format(dapi_constants.BODY["250char"]),
        }

        url = "{}/threads".format(self.url_prefix)
        response = self.client.post(
            url=url,
            data=json.dumps(body),
            headers=self._post_headers,
            name="POST_thread",
            verify=False
        )

        self.verify_response(response, url)
        return response.json()

    def create_response(self, thread_id):
        """
        POST a response (1st level comment) and adds the id to the response list

        Args:
            thread_id (str): The id of the thread to create a response for

        Returns:
            (dict): The comment.
        """
        url = "{}/comments".format(self.url_prefix)
        body = {
            "thread_id": thread_id,
            "raw_body": "Orphaned comment aka Batman. {}".format(dapi_constants.BODY["250char"]),
        }
        response = self.client.post(
            url=url,
            data=json.dumps(body),
            headers=self._post_headers,
            name="POST_comment_response"
        )
        self.verify_response(response, url)
        return response.json()

    def create_comment(self, comment_id, thread_id):
        """
        POST a comment (2nd level comment) to the response list

        Args:
            comment_id (str): the id of the response to create the comment for
            thread_id (str): The id of the thread to create the comment for

        Returns:
            (dict): The comment.
        """
        url = "{}/comments".format(self.url_prefix)
        body = {
            "parent_id": comment_id,
            "thread_id": thread_id,
            "raw_body": "Orphaned comment aka Batman. {}".format(dapi_constants.BODY["250char"]),
        }
        response = self.client.post(
            url=url,
            data=json.dumps(body),
            headers=self._post_headers,
            name="POST_comment_comment"
        )

        self.verify_response(response, url)
        return response.json()

    def get_comment_and_response_count(self, thread_id):
        """
        Returns the comment_count and response_count for a Thread

        This helper method is used when requiring verbose outputs for threads
        that have high comment_counts. For example, a response with
        1000 comment.

        Args:
            thread_id (str): Thread to get the comment_count and response_count

        Returns:
            (tuple): (comment_count, response_count)
        """
        url = "{}/threads/{}/".format(self.url_prefix, thread_id)
        response = self.client.get(url, verify=False, name="GET_thread")
        self.verify_response(response, url)
        response = response.json()
        return response["comment_count"], response["response_count"]

    def patch_thread(self, thread_id, data, name):
        """
        PATCHes a thread

        Args:
            thread_id (str): Thread to patch
            data (dict): The data to patch with
            name (str): Name to show for request

        Returns:
            (dict): The thread
        """
        url = "{}/threads/{}/".format(self.url_prefix, thread_id)
        response = self.client.patch(
            url,
            data=json.dumps(data),
            verify=False,
            headers=self._headers,
            name=name
        )
        self.verify_response(response, url)
        return response.json()

    def patch_comment(self, comment_id, data, name):
        """
        PATCHes a comment

        Args:
            comment_id (str): Comment to patch
            data (dict): The data to patch with
            name (str): Name to show for request

        Returns:
            (dict): The comment
        """
        url = "{}/comment/{}/".format(self.url_prefix, comment_id)
        response = self.client.patch(
            url,
            data=json.dumps(data),
            verify=False,
            headers=self._headers,
            name=name
        )
        self.verify_response(response, url)
        return response.json()

    def delete_thread(self, thread_id):
        """
        DELETE a thread

        Args:
            thread_id (str): Thread to patch
        """
        url = "{}/threads/{}/".format(self.url_prefix, thread_id)
        self.client.delete(
            url,
            verify=False,
            headers=self._headers,
            name="DELETE_thread"
        )

    def delete_comment(self, comment_id):
        """
        DELETE a comment

        Args:
            comment_id (str): Comment to patch
        """
        url = "{}/comments/{}/".format(self.url_prefix, comment_id)
        self.client.delete(
            url,
            verify=False,
            headers=self._headers,
            name="DELETE_comment"
        )
