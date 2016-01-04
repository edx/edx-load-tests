import json
import os
import requests
import time
import urllib

BASIC_AUTH_CREDENTIALS = None
if 'BASIC_AUTH_USER' in os.environ and 'BASIC_AUTH_PASSWORD' in os.environ:
    BASIC_AUTH_CREDENTIALS = (
        os.environ['BASIC_AUTH_USER'],
        os.environ['BASIC_AUTH_PASSWORD']
    )


class PostCreationException(Exception):
    """Raised when the creation of a post fails"""
    pass


class DiscussionsSeeder(object):

    def __init__(self,
                 course_id=None,
                 lms_url=None):
        self.lms_url = lms_url
        self.sess = requests.Session()
        self.course_id = course_id
        self.raw_body = "Arthur looked up. 'Ford!' he said, 'there's an infinite number of monkeys outside who want to talk to us about this script for Hamlet they've worked out."
        if BASIC_AUTH_CREDENTIALS is not None:
            self.sess.auth = BASIC_AUTH_CREDENTIALS

    def get_csrf(self, url):
        """
        return csrf token retrieved from the given url
        """
        try:
            response = self.sess.get(url)
            csrf = response.cookies['csrftoken']
            return {'X-CSRFToken': csrf, 'Referer': url}
        except Exception as error:  # pylint: disable=W0703
            print "Error when retrieving csrf token.", error

    def login_to_lms(self, email, password):
        """
        Use given credentials to login to studio.

        Args:
            email (str): Login email
            password (str): Login password
        """
        signin_url = '{}/login'.format(self.lms_url)
        headers = self.get_csrf(signin_url)
        login_url = '%s/login_ajax' % self.lms_url
        print 'Logging in to %s' % self.lms_url

        response = self.sess.post(login_url, {
            'email': email,
            'password': password,
            'honor_code': 'true'
        }, headers=headers).json()

        if not response['success']:
            raise Exception(str(response))

        print 'Login successful'

    def seed_comments(self, course_id, posts, responses, child_comments):
        """
        #Creates 20 comments to a response for n posts

        Args:
            course_id (str): The courses identifier
        """
        topic_id = "course"
        body = {
            "course_id": course_id,
            "topic_id": topic_id,
            "type": "discussion",
            "title": "Thread with R-C {}-{}".format(responses, child_comments),
            "raw_body": "This is a thread. {}".format(self.raw_body),
        }

        thread_list = []
        for p in range(0, posts):
            thread_id = self.create_thread(body)
            thread_list.append(thread_id)

            for i in range(0, responses):
                #big_thread = self.create_thread(body)
                #thread_list.append(big_thread)

                comment_id = self.create_comment(thread_id)

                #for j in range(0, ((i + 1) * 20)):
                for j in range(0, child_comments):
                    self.create_comment(thread_id, comment_is_child=comment_id)
            #print "Created thread {} of {} with {} comments".format(p, posts, str((i + 1) * 20))
            print "Created thread {} of {} with {} responses and {} comments".format(p, posts, responses, child_comments)
        return thread_list

    def seed_threads(self, course_id, posts):
        """
        Creates some test threads/comments in the first

        Args:
            course_key (str): The courses identifier
            posts (int): Posts to be created in multiples of 10
        """
        # topic_id = self.get_first_course_topic(course_key)
        topic_id = "course"
        body = {
            "course_id": course_id,
            "topic_id": topic_id,
            "type": "discussion",
            "title": "default thread",
            "raw_body": "This is a thread. {}".format(self.raw_body),
        }

        # Create 10 Threads
        for i in range(0, posts):
            self.create_thread(body)
            self.create_thread(body)
            self.create_thread(body, question=True)
            self.create_thread(body, question=True)
            self.create_toggled_field(field="following", post_type="threads", id=self.create_thread(body))
            self.create_toggled_field(field="voted", post_type="threads", id=self.create_thread(body))
            self.create_toggled_field(field="abuse_flagged", post_type="threads", id=self.create_thread(body))
            thread_id = self.create_thread(body)
            comment_id = self.create_comment(thread_id)
            self.create_comment(thread_id, comment_is_child=comment_id)
            for j in range(0, 2):
                thread_id = self.create_thread(body)
                self.create_comment(thread_id)
            print "Created {} of {} posts".format(((i + 1) * 10), posts * 10)

    def create_thread(self, body, question=False):
        url = "{}/api/discussion/v1/threads/".format(self.lms_url)
        if question:
            body["type"] = "question"
        response = self.sess.post(
            url=url,
            data=json.dumps(body),
            headers=self._post_headers(url=url)
        )
        if response.status_code == 500:
            raise PostCreationException(response.status_code + ":" + response.content)
        return response.json()["id"]

    def create_toggled_field(self, field, post_type, id):
        url = "{}/api/discussion/v1/{}/{}/".format(self.lms_url, post_type, id)
        body = {
            field: "true",
            "raw_body": "post type should be {}, {} should be true. {}".format(post_type, field, self.raw_body)
        }
        response = self.sess.patch(
            url=url,
            data=json.dumps(body),
            headers=self._post_headers(url=url,content_type='application/merge-patch+json')
        )
        if response.status_code == 500:
            raise PostCreationException(response.status_code)
        return response.json()["id"]

    def create_comment(self, thread_id, comment_is_child=None):
        url = "{}/api/discussion/v1/comments/".format(self.lms_url)
        body = {
            "thread_id": thread_id,
            "raw_body": "Orphaned comment aka Batman. {}".format(self.raw_body),
        }
        if comment_is_child:
            body["parent_id"] = comment_is_child
            body["raw_body"] = "Comment with parent. {}".format(self.raw_body),
        response = self.sess.post(
            url=url,
            data=json.dumps(body),
            headers=self._post_headers(url=url)
        )
        if response.status_code == 500:
            raise PostCreationException(response.status_code)

        return response.json()["id"]

    def create_thread_data_file(self, file_name, course_id, thread_id_list):
        """
        Creates a file with the thread_ids for given course_id

        Args:
            course_id (str): ID of the course we want all the thread_ids from
            file_name (str): Name of the file to save to
        """
        if not thread_id_list:
            course_id = urllib.quote_plus(course_id)
            url = "{}/api/discussion/v1/threads/?course_id={}&page_size=100".format(self.lms_url, course_id)
            response = self.sess.get(url)\

            if response.status_code != 200:
                print "{}: {}".format(response.status_code, response.content[0:200])
                return

            response = response.json()

            thread_id_list = []
            for thread in response["results"]:
                thread_id_list.append(thread["id"])
            while response["next"]:
                next_page_url = response["next"]
                response = self.sess.get(next_page_url)
                while response.status_code != 200:
                    print "{}: Could not get next in response. Trying again in 5 seconds".format(response.status_code)
                    time.sleep(5)
                    response = self.sess.get(next_page_url)
                response = response.json()
                if response["next"]:
                    print "GETting page {}".format(response["next"].split("&page=")[1])
                for thread in response["results"]:
                    thread_id_list.append(thread["id"])

        with open(file_name, 'w') as file_:
            l = len(thread_id_list)
            i = 1
            for thread_id in thread_id_list:
                file_.write(thread_id + "\n")
                if (i % 100) == 0:
                    print "Saving Thread {} of {}".format(i, l)

    def _post_headers(self, url, content_type='application/json', accept='application/json'):
        """Headers for a POST request, including the CSRF token. """
        return {
            'Content-type': content_type,
            'Accept': accept,
            'X-CSRFToken': self.sess.cookies.get('csrftoken', ''),
            'Referer': url
        }
