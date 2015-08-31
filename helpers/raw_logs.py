import os

from csv import DictWriter
from datetime import datetime
from locust import events
from tempfile import NamedTemporaryFile

LOG_FILE_NAME = "requests-{testid}-{pid}-{state}.log"
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

# A value between 0 and 1 that specifies what fraction of metrics
# to log.
METRIC_RESOLUTION = float(os.environ.get('METRIC_RESOLUTION', 1))


class RawLogger(object):
    def __init__(self):
        events.request_success += self.on_request_success
        events.request_failure += self.on_request_failure
        events.reconfigure += self.on_reconfigure
        events.hatch_complete += self.on_hatch_complete
        self.logfile = None
        self.csvwriter = None
        self._metric_counter = 0
        self.hatching = True

    def _open_log_file(self):
        if self.logfile is None:
            self.logfile = open(LOG_FILE_NAME.format(
                testid=self.testid,
                state='hatching' if self.hatching else 'running',
                pid=os.getpid(),
            ), 'wb')
            self.csvwriter = DictWriter(
                self.logfile,
                LOG_FIELDS,
                extrasaction='ignore',
            )
            self.csvwriter.writeheader()

    def _close_log_file(self):
        if self.logfile is not None:
            self.logfile.close()
        self.logfile = None
        self.csvwriter = None

    def on_reconfigure(self, testid, **kwargs):
        self.testid = testid

        self._close_log_file()

    def on_request_success(self, **kwargs):
        if self._skip_entry():
            return

        self._open_log_file()
        kwargs['result'] = 'success'
        self.csvwriter.writerow(kwargs)

    def on_request_failure(self, **kwargs):
        if self._skip_entry():
            return

        self._open_log_file()
        kwargs['result'] = 'failure'
        if 'exception' in kwargs:
            kwargs['exception'] = unicode(kwargs['exception'])
        self.csvwriter.writerow(kwargs)

    def on_hatch_complete(self, **kwargs):
        self.hatching = False
        self._metric_counter = 0
        self._close_log_file()

    def _skip_entry(self):
        """
        Return True if the logger should skip this entry.
        """
        self._metric_counter += METRIC_RESOLUTION
        record = self._metric_counter >= 1
        if record:
            self._metric_counter -= 1
        return not record
