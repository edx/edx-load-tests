"""
Code to capture all Locust request results in MongoDB.

To capture all your Locust request data, simply add these lines to your locustfile.py:

from raw_data_capture import RequestDatabaseLogger
db_evts = RequestDatabaseLogger()
db_evts.activate()

Optionally, add MongoDB connection information as so:

db_evts = RequestDatabaseLogger(mongo_host='localhost', mongo_port=27107)

If the import fails, you'll need to add a path to it before the import using something as below:

# Work around the fact that this code doesn't live in a proper Python package.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'helpers'))
"""

import os
import socket
import datetime
import pymongo
from itertools import chain
from locust import runners, events as locust_events


class MongoConnection(object):
    """
    Base class for connecting to MongoDB.
    """
    def __init__(self, db, host, port=27017, tz_aware=True, user=None, password=None, **kwargs):
        """
        Create & open the connection - and authenticate.
        """
        self.database = pymongo.database.Database(
            pymongo.MongoClient(
                host=host,
                port=port,
                tz_aware=tz_aware,
                **kwargs
            ),
            db
        )

        if user is not None and password is not None:
            self.database.authenticate(user, password)


class RequestDatabaseLogger(object):
    """
    Class to log raw locust request data (both successes and failures) to MongoDB.
    Buffers the data and inserts it in batches to MongoDB.
    """
    # Flush request data events only after this many have been collected.
    EVENTS_BEFORE_FLUSH = 10

    # Enum of request outcomes.
    REQ_SUCCESS = 'success'
    REQ_FAILURE = 'failure'

    # MongoDB database info
    DB_NAME = 'locust_data'
    COLLECTION_NAME = 'requests'
    TEST_RUNS_COLLECTION = 'test_runs'

    def __init__(self, mongo_host='localhost', mongo_port=27017):
        # Add list of request data.
        self._successes = []
        self._failures = []

        # Make a unique identifier for this Locust client.
        self.client_id = "{}:{}".format(socket.gethostname(), os.getpid())

        self.db = MongoConnection(db=self.DB_NAME, host=mongo_host, port=mongo_port)
        self.req_data = self.db.database[self.COLLECTION_NAME]
        self.test_runs = self.db.database[self.TEST_RUNS_COLLECTION]

    def _apply_event(self, event_list, result, request_type, name, response_time, response_length, exception):
        event_data = {
            'result': result,
            'type': request_type,
            'name': name,
            'response_time': response_time,
            'response_length': response_length,
            'exception': exception,
            'client_id': self.client_id,
            'timestamp': datetime.datetime.utcnow()
        }
        event_list.append(event_data)

        # Check if list is big enough to insert.
        if len(event_list) >= self.EVENTS_BEFORE_FLUSH:
            self.req_data.insert(event_list)
            return True

        return False

    def _sort_stats(self, stats):
        return [stats[key] for key in sorted(stats.iterkeys())]

    def _gather_request_stats(self):
        """
        Gather all the statistics about requests in the test.
        """
        headers = [
            'Method',
            'Name',
            '# requests',
            '# failures',
            'Median response time',
            'Average response time',
            'Min response time',
            'Max response time',
            'Average Content Size',
            'Requests/s',
        ]

        rows = []
        for s in chain(self._sort_stats(runners.locust_runner.request_stats), [runners.locust_runner.stats.aggregated_stats("Total", full_request_history=True)]):
            rows.append([
                s.method,
                s.name,
                s.num_requests,
                s.num_failures,
                s.median_response_time,
                s.avg_response_time,
                s.min_response_time or 0,
                s.max_response_time,
                s.avg_content_length,
                s.total_rps,
            ])
        return headers, rows

    def _gather_distribution_stats(self):
        """
        """
        headers = [
            'Name',
            '# requests',
            '50%',
            '66%',
            '75%',
            '80%',
            '90%',
            '95%',
            '98%',
            '99%',
            '100%',
        ]
        rows = []
        for s in chain(self._sort_stats(runners.locust_runner.request_stats), [runners.locust_runner.stats.aggregated_stats("Total", full_request_history=True)]):
            if s.num_requests:
                #rows.append(s.percentile(tpl='%s,%i,%i,%i,%i,%i,%i,%i,%i,%i,%i').split(','))
                stats = []
                for x in s.percentile(tpl='%s,%i,%i,%i,%i,%i,%i,%i,%i,%i,%i').split(','):
                    try:
                        stats.append(int(x))
                    except ValueError:
                        stats.append(x)
                rows.append(stats)
            else:
                rows.append([s.name, 0, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"])
        return headers, rows


    def master_start_hatching_handler(self):
        # Make an ID for this test run. Use this for all raw data captured.
        # Just use the datetime down to the second.
        start_time = datetime.datetime.now()
        format = '%Y%m%d_%H%M%S'
        self.run_id = start_time.strftime(format)
        test_run_data = {
            '_id': self.run_id,
            'start_time': start_time
        }
        self.test_runs.insert(test_run_data)

    def master_stop_hatching_handler(self):
        # Save the stop time of the test.
        finish_time = datetime.datetime.now()

        # Save the Locust test information - the stuff usually sent to CSV.
        request_stats = self._gather_request_stats()
        distribution_stats = self._gather_distribution_stats()
        self.test_runs.update(
            {'_id': self.run_id},
            {'$set':
                {
                    'finish_time': finish_time,
                    'request_stats': {'headers': request_stats[0], 'data': request_stats[1]},
                    'distribution_stats': {'headers': distribution_stats[0], 'data': distribution_stats[1]}
                }
            }
        )

        # Rename the collection containing all the raw request data.
        self.req_data.rename('{}_{}'.format(self.COLLECTION_NAME, self.run_id))

    def success_handler(self, request_type, name, response_time, response_length, **kwargs):
        # Add to list.
        if self._apply_event(
            self._successes, self.REQ_SUCCESS,
            request_type, name, response_time, response_length, None
        ):
            # If events were inserted, clear the list.
            self._successes = []

    def failure_handler(self, request_type, name, response_time, exception, **kwargs):
        # Add to list.
        if self._apply_event(
            self._failures, self.REQ_FAILURE,
            request_type, name, response_time, None, unicode(exception)
        ):
            # If events were inserted, clear the list.
            self._failures = []

    def flush(self):
        """
        Flush all remaining events to the database.
        """
        if len(self._successes):
            self.req_data.insert(self._successes)
        if len(self._failures):
            self.req_data.insert(self._failures)
        self._successes = self._failures = []

    def activate(self):
        """
        Register all event handlers.
        """
        locust_events.master_start_hatching += self.master_start_hatching_handler
        locust_events.master_stop_hatching += self.master_stop_hatching_handler
        locust_events.request_success += self.success_handler
        locust_events.request_failure += self.failure_handler
        locust_events.quitting += self.flush


