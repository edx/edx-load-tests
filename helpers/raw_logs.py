import os

from csv import DictWriter
from datetime import datetime
from locust import events
from tempfile import NamedTemporaryFile

LOG_FILE_NAME = "requests-{testid}-{pid}.log"
LOG_FIELDS = [
    "start_time",
    "end_time",
    "request_type",
    "name",
    "result",
    "response_time",
    "response_length",
    "exception",
]


class RawLogger(object):
    def __init__(self):
        events.request_success += self.on_request_success
        events.request_failure += self.on_request_failure
        events.reconfigure += self.on_reconfigure
        self.logfile = None
        self.csvwriter = None

    def _open_log_file(self):
        if self.logfile is None:
            self.logfile = open(LOG_FILE_NAME.format(testid=self.testid, pid=os.getpid()), 'wb')
            self.csvwriter = DictWriter(
                self.logfile,
                LOG_FIELDS,
                extrasaction='ignore',
            )
            self.csvwriter.writeheader()

    def on_reconfigure(self, testid, **kwargs):
        self.testid = testid

        if self.logfile is not None:
            self.logfile.close()

        self.logfile = None
        self.csvwriter = None

    def on_request_success(self, **kwargs):
        self._open_log_file()
        kwargs['result'] = 'success'
        self.csvwriter.writerow(kwargs)

    def on_request_failure(self, **kwargs):
        self._open_log_file()
        kwargs['result'] = 'failure'
        if 'exception' in kwargs:
            kwargs['exception'] = unicode(kwargs['exception'])
        self.csvwriter.writerow(kwargs)
