"""
These tests are meant to model the real ways in which a user interacts
with the student notes feature.  Currently there are five actions a
learner can take in student notes:

    - Create a note
    - Edit a note
    - Delete a note
    - Browse notes in the notes tab
    - Search notes in the notes tab

There are many TaskSets for interacting with particular parts of
student notes.  The `LmsNotesTasks` TaskSet attempts to model how an
average user might interact with student notes.
"""
import os
import sys

# due to locust sys.path manipulation, we need to re-add the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from contextlib import contextmanager
import json
from locust import HttpLocust, task, TaskSet
import logging
import random

from helpers import settings
# NOTE: the host URL passed in via command-line '--host' flag is the host of
# the LMS!  Make sure to set the notes service URL via the NOTES_HOST setting.
settings.init(__name__, required_data=[
    'courses',
    'NOTES_HOST',
    'NUM_NOTES',
    'NUM_WORDS',
    'NUM_TAGS',
    'NUM_SEARCH_TERMS',
    'LOCUST_TASK_SET',
    'LOCUST_MIN_WAIT',
    'LOCUST_MAX_WAIT'
])

from helpers.mixins import EnrollmentTaskSetMixin
from helpers.edx_app import EdxAppTasks

# Constants used by the LMS when searching student notes.
HIGHLIGHT_TAG = 'span'
HIGHLIGHT_CLASS = 'note-highlight'

# Internal constants
DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), 'notes_data/')
with open(os.path.join(DATA_DIRECTORY, 'basic_words.txt')) as f:
    NOTES_TEXT = [word for line in f for word in line.split()]

log = logging.getLogger(__name__)


def pick_some(sequence, num_items):
    """
    Return a list of between 1 and `num_items` (inclusive) items from
    `sequence`.
    """
    return random.sample(sequence, random.randint(1, num_items))


class BaseNotesTask(EdxAppTasks, EnrollmentTaskSetMixin):
    """
    Base class for all TaskSet classes which interact with student notes.
    """
    def __init__(self, *args, **kwargs):
        """
        Keep track of notes we post.
        """
        super(BaseNotesTask, self).__init__(*args, **kwargs)
        self._notes = {}

    def on_start(self):
        """
        Runs before any requests are made.
        """
        self.auto_auth()
        self.enroll(self.course_id)

    @property
    def annotator_auth_token(self):
        """
        Get the JWT key for making requests to the notes service from the LMS.
        """
        return self.client.get(
            '/courses/{course_id}/edxnotes/token/'.format(course_id=self.course_id),
            headers={'content-type': 'text/plain'},
        ).content

    @contextmanager
    def get_posted_student_note(self, warning_message):
        """
        Yield a note that the current locust has created.  If there are none
        left, create a new note and yield it.
        """
        try:
            yield self._notes[random.choice(self._notes.keys())]
        except IndexError:  # No notes remaining
            log.debug(warning_message)
            yield self._create_note()

    def _request_from_notes_service(self, method, path, params_or_body=None, **kwargs):
        """
        Internal helper for making a request to the notes service.

        Arguments:
            method (str): HTTP method to execute.
            path (str): URL path to the resource being requested.
            params_or_body (dict): Dict of data to pass in the request.
        Returns:
            response: Response to the request that was made.
        """
        method = method.lower()
        # Pass in the JWT token and CSRF token from edx platform
        kwargs.update({
            'headers': {
                'x-annotator-auth-token': self.annotator_auth_token,
                'X-CSRFToken': self.client.cookies.get('csrftoken', ''),
                'content-type': 'application/json',
            },
        })
        if params_or_body is not None:
            if method == 'get':
                kwargs.update({'params': params_or_body})
            elif method in ['post', 'patch', 'put', 'delete']:
                kwargs.update({'data': json.dumps(params_or_body)})
        return getattr(self.client, method)(
            settings.data['NOTES_HOST'] + path,
            **kwargs
        )

    def get(self, path, params=None, **kwargs):
        """
        Internal helper for making a GET request to the notes service.
        """
        return self._request_from_notes_service('get', path, params, **kwargs)

    def post(self, path, body=None, **kwargs):
        """
        Internal helper for making a POST request to the notes service.
        """
        return self._request_from_notes_service('post', path, body, **kwargs)

    def put(self, path, body=None, **kwargs):
        """
        Internal helper for making a PUT request to the notes service.
        """
        return self._request_from_notes_service('put', path, body, **kwargs)

    def delete(self, path, params=None, **kwargs):
        """
        Internal helper for making a DELETE request to the notes service.
        """
        return self._request_from_notes_service('delete', path, params, **kwargs)

    def _create_note(self):
        """
        Post a note containing random text to the notes service.  Because of
        the complex and unnecessary nature of scraping course text, the 'text',
        'tags', and 'quote' fields will be arbitrarily generated.
        """
        data = {
            'user': self._anonymous_user_id,
            'course_id': self.course_id,
            'text': ' '.join(pick_some(
                NOTES_TEXT,
                settings.data['NUM_WORDS'],
            )),
            'tags': pick_some(
                NOTES_TEXT,
                settings.data['NUM_TAGS'],
            ),
            'quote': ' '.join(pick_some(NOTES_TEXT, 5)),
            'usage_id': self.course_data.html_usage_id,
            'ranges': [
                {
                    'start': '/div[1]/p[1]',
                    'end': '/div[1]/p[1]',
                    'startOffset': 0,
                    'endOffset': 6
                }
            ],
        }
        dump_data = json.dumps(data)
        data_json = json.loads(dump_data)
        print data_json
        note = json.loads(self.post("/api/v1/annotations/", data).content)
        #note = json.loads(self.post('/api/v1/annotations/', data).content)
        self._notes[note['id']] = note
        return note

    def _create_many_notes(self, num_notes):
        """
        Create many notes within the course for the current user.
        """
        for _ in xrange(num_notes):
            self._create_note()

    def _delete_note(self):
        """
        Delete a note.
        """
        collection_path = '/api/v1/annotations/'
        with self.get_posted_student_note('No notes left to delete.') as note:
            self.delete(collection_path + note['id'], note, name=collection_path + '[id]')
            self._notes.pop(note['id'])

    def _edit_note(self):
        """
        Edit a note.
        """
        collection_path = '/api/v1/annotations/'
        with self.get_posted_student_note('No notes left to edit.') as note:
            note['text'] = ' '.join(pick_some(
                NOTES_TEXT,
                settings.data['NUM_WORDS'],
            ))
            self.put(collection_path + note['id'], note, name=collection_path + '[id]')
            self._notes[note['id']] = note

    def _list_notes(self):
        """
        List notes in the LMS.
        """
        path = '/courses/{course_id}/edxnotes/'.format(course_id=self.course_id)
        self.client.get(path, verify=False)

    def _search_notes(self):
        """
        Search notes from the LMS for random text.
        """
        path = '/courses/{course_id}/edxnotes/search/'.format(course_id=self.course_id)
        params = {
            'text': ' '.join(pick_some(
                NOTES_TEXT,
                settings.data['NUM_SEARCH_TERMS'],
            )),
        }
        # Custom name ensures searches are grouped together in locust results.
        self.client.get(path, params=params, name=path + '?text=[search_text]', verify=False)

    @property
    def is_child(self):
        """
        Return True if this TaskSet is a child of another TaskSet
        """
        return isinstance(self.parent, TaskSet)


class ModifyNotesTasks(BaseNotesTask):
    """
    Create, edit, and delete notes with weighted probabilities.
    """
    @task(10)
    def create_note(self):
        """
        Create a note.
        """
        self._create_note()

    @task(2)
    def delete_note(self):
        self._delete_note()

    @task(3)
    def edit_note(self):
        self._edit_note()


class ListLmsNotesTasks(BaseNotesTask):
    """
    List notes on the LMS notes tab.
    """
    def on_start(self):
        """
        Create a constant number of notes
        """
        super(ListLmsNotesTasks, self).on_start()
        self._create_many_notes(settings.data['NUM_NOTES'])

    @task(10)
    def list_notes(self):
        self._list_notes()

    @task(1)
    def stop(self):
        if self.is_child:
            self.interrupt()


class SearchLmsNotesTasks(BaseNotesTask):
    """
    Search the notes API through the LMS, as a user would.
    """
    def on_start(self):
        """
        Create a constant number of notes
        """
        super(SearchLmsNotesTasks, self).on_start()
        self._create_many_notes(settings.data['NUM_NOTES'])

    @task(10)
    def search_notes(self):
        self._search_notes()

    @task(1)
    def stop(self):
        if self.is_child:
            self.interrupt()


class BrowseLmsNotesTasks(TaskSet):
    """
    Parent TaskSet for viewing the notes list and searching the notes list.
    """
    tasks = {ListLmsNotesTasks: 3, SearchLmsNotesTasks: 1}


class LmsNotesTasks(BaseNotesTask):
    """
    Parent TaskSet modeling how users might interact with student
    notes overall.
    """
    @task(10)
    def create_note(self):
        self._create_note()

    @task(2)
    def delete_note(self):
        self._delete_note()

    @task(3)
    def edit_note(self):
        self._edit_note()

    @task(30)
    def list_notes(self):
        self._list_notes()

    @task(10)
    def search_notes(self):
        self._search_notes()


class SearchApiNotesTasks(BaseNotesTask):
    """
    Search the notes API directly.
    """
    @task
    def search_notes(self):
        """
        Search notes for random text.
        """
        path = '/api/v1/search/'
        self.get(
            path,
            {
                'user': self._anonymous_user_id,
                'course_id': self.course_id,
                'text': ' '.join(pick_some(
                    NOTES_TEXT,
                    settings.data['NUM_SEARCH_TERMS'],
                )),
                'highlight': True,
                'highlight_tag': HIGHLIGHT_TAG,
                'highlight_class': HIGHLIGHT_CLASS
            },
            name=path + '?text=[search_text]'
        )


class NotesLocust(HttpLocust):
    task_set = globals()[settings.data['LOCUST_TASK_SET']]
    min_wait = settings.data['LOCUST_MIN_WAIT']
    max_wait = settings.data['LOCUST_MAX_WAIT']
