import json
import random
import urllib

import dapi_constants


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
    #course_id = "course_id={}".format(urllib.quote_plus(self.course_id))
    course_id = "course_id=course-v1%3AedX%2BDemoX%2BDemo_Course"
    following = "following={}".format(random.choice(dapi_constants.FOLLOWING))
    view = "view={}".format(random.choice(dapi_constants.VIEW))

    page_size = "page_size={}".format(page_size) if page_size else "page_size={}".format(random.choice(dapi_constants.PAGE_SIZE))
    page = "page={}".format(page) if page else "page={}".format(random.choice(dapi_constants.PAGE))

    order_by = "order_by={}".format("comment_count" if prioritize_comments else random.choice(dapi_constants.ORDER_BY))
    order_direction = "order_direction={}".format("desc" if prioritize_comments else random.choice(dapi_constants.ORDER_DIRECTION))

    # url = "/api/discussion/v1/threads/?{}&{}&{}&{}&{}&{}".format(
    #     course_id,
    #     following,
    #     # view, # causing 500 for some reason
    #     order_by,
    #     order_direction,
    #     page,
    #     page_size,
    # )

    url = "/api/discussion/v1/threads/?{}&{}&{}&{}&{}".format(
        course_id,
        order_by,
        order_direction,
        page,
        page_size,
    )

    name = url if verbose else "GET_thread_list"

    response = self.client.get(url=url, verify=False, name=name)

    if response.status_code == 200:
        if response.json()["results"]:
            if prioritize_comments:
                threads_with_comments = []
                for thread in response.json()["results"]:
                    if thread["comment_count"] > 0:
                        threads_with_comments.append(thread)
                if threads_with_comments:
                    return random.choice(threads_with_comments)
            return random.choice(response.json()["results"])
        return None
    else:
        print url
        print "{}: {}".format(response.status_code, response.content[0:200])
        return None


def get_random_comment(self, thread, verbose=False):
    """
    Common method for GETting a comment list, returns the comment

    Similar to _get_thread, GETting a comment happens significantly more
    than other HTTP requests so this method will be used to retrieve
    comment data.

    Args:
        thread (dict): The thread we are getting hte comment from
        verbose (Bool): Get detailed locust request names
    """
    #  These parameters did seem to affect response times 09/29/16
    page_size = "page_size={}".format(random.choice(dapi_constants.PAGE_SIZE))

    url = "/api/discussion/v1/comments/?thread_id={}&{}".format(
        thread["id"],
        page_size,
        # mark_as_read,
        # page
    )

    # Required for question threads, set to False for discussion
    if thread["type"] == "question":
        #endorsed = "endorsed=False"  # unless set to false, no comments are returned since endorse is not seeded
        url = "{}&endorsed=False".FORMAT(url)
    #else:
    #    endorsed = "endorsed=None"

    #  These parameters did not seem to affect response times 09/29/16
    # mark_as_read = "mark_as_read={}".format(random.choice(dapi_constants.MARK_AS_READ))
    # page = "page={}".format(random.choice(dapi_constants.PAGE))

    # url = "/api/discussion/v1/comments/?thread_id={}&{}&{}".format(
    #     thread["id"],
    #     page_size,
    #     endorsed,
    #     # mark_as_read,
    #     # page
    # )

    # Only be useful when running task in isolation with pre-set comment data
    if verbose:
        comment_count, response_count = self._get_comment_and_response_count(thread["id"])
        name = "comment_count={}_response_count={}".format(comment_count, response_count)
    else:
        name = "GET_comment_list"

    response = self.client.get(url, verify=False, name=name)

    if response.status_code == 200:
        if response.json()["results"]:
            return random.choice(response.json()["results"])
        return None
    else:
        print url
        print "{}: {}".format(response.status_code, response.content[0:200])
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

    url = "/api/discussion/v1/threads"
    response = self.client.post(
        url=url,
        data=json.dumps(body),
        headers=self._post_headers,
        name="POST_thread",
        verify=False
    )

    if response.status_code == 200:
        return response
    else:
        print url
        print "{}: {}".format(response.status_code, response.content[0:200])


def create_response(self, thread_id):
    """
    POST a response (1st level comment) and adds the id to the response list

    Args:
        thread_id (str): The id of the thread to create a response for
    """
    url = "/api/discussion/v1/comments"
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
    if response.status_code != 200:
        print url
        print "{}: {}".format(response.status_code, response.content[0:200])
    return response.json()


def create_comment(self, comment_id, thread_id):
    """
    POST a comment (2nd level comment) to the response list

    Args:
        comment_id (str): the id of the response to create the comment for
        thread_id (str): The id of the thread to create the comment for
    """
    url = "/api/discussion/v1/comments/"
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

    if response.status_code != 200:
        print url
        print "{}: {}".format(response.status_code, response.content[0:200])
    return response.content
