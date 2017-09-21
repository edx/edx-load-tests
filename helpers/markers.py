"""
This module causes logging of test start/stop and other critical events.

The locust logging format is not necessarily stable, so we use the event hooks
API to implement our own "stable" logging for later programmatic reference.

Enable this feature in a load test by including the following lines in some
form, near the begginning of the locustfile:

    from helpers import markers
    markers.install_event_markers()

As of this writing, the events are:

* locust_start_hatching
* master_start_hatching
* quitting
* hatch_complete
* edx_heartbeat
"""
import re
import logging
import yaml
from datetime import datetime, timedelta

LOG = logging.getLogger(__name__)

INTERMEDIATE_SUMMARY_FILENAME = 'results/intermediate_summary.yml'

# As of this writing, locust prefixes logs using the default datefmt used by
# the python logging library:
# https://github.com/locustio/locust/blob/v0.7.5/locust/log.py#L13
# https://github.com/python/cpython/blob/master/Lib/logging/__init__.py#L492
LOCUST_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S,%f'

class EventMarker(object):
    """
    Simple event marker that logs on every call.
    """
    def __init__(self, name):
        self.name = name

    def _generate_log_message(self):
        LOG.info('locust event: {}'.format(self.name))

    def __call__(self, *args, **kwargs):
        self._generate_log_message()


class HeartbeatEventMarker(EventMarker):
    """
    Event marker which behaves like a heartbeat.

    This marker implements a rate limit on logging to prevent flooding logs.
    """
    def __init__(self, name='edx_heartbeat', period=timedelta(seconds=30)):
        super(HeartbeatEventMarker, self).__init__(name)
        self.period = period
        self._last_heartbeat = None

    def __call__(self, *args, **kwargs):
        if not self._last_heartbeat:
            self._last_heartbeat = datetime.now()
        elif self._last_heartbeat + self.period < datetime.now():
            self._generate_log_message()
            self._last_heartbeat = datetime.now()


def quitting_handler():
    """
    """
    # "import locust" within this scope so that this module is importable by
    # code running in environments which do not have locust installed.
    import locust
    num_errors = sum(e.occurences for e in locust.stats.global_stats.errors.values())
    locust_counts = {
        'num_requests': locust.stats.global_stats.num_requests,
        'num_failures': locust.stats.global_stats.num_failures,
        'num_errors': num_errors,
    }
    with open(INTERMEDIATE_SUMMARY_FILENAME, 'w') as f:
        yaml.dump(locust_counts, stream=f)


def install_event_markers():
    """
    Call this function from a locustfile to enable event markers in logging.
    """
    # "import locust" within this scope so that this module is importable by
    # code running in environments which do not have locust installed.
    import locust

    # Install simple event markers
    locust.events.locust_start_hatching += EventMarker('locust_start_hatching')
    locust.events.master_start_hatching += EventMarker('master_start_hatching')
    locust.events.quitting += EventMarker('quitting')
    locust.events.hatch_complete += EventMarker('hatch_complete')

    # Install heartbeat markers which are rate limited
    heartbeat_handler = HeartbeatEventMarker()
    locust.events.request_success += heartbeat_handler
    locust.events.request_failure += heartbeat_handler

    # Install handler which reports basic success/failure statistics for later
    # consumption.
    locust.events.quitting += quitting_handler


def parse_logfile_event_marker(line_str):
    """
    Parse a logfile line as an event marker.

    Parameters:
        line_str (str): a line from the locust log for a load test with markers
            enabled.

    Returns:
        dict: dict object with the following keys: 'time' (value is
            datetime.datetime), and 'event' (value is string).
    """
    match = re.match(
        '\[(.+)\] .+/INFO/{}: locust event: (.*)$'.format(re.escape(__name__)),
        line_str,
    )
    obj = None
    if match:
        timestamp, event = match.group(1, 2)
        obj = {
            # Assume logging is UTC, and return tz-unaware datetime object
            # which implies UTC.
            'time': datetime.strptime(timestamp, LOCUST_TIMESTAMP_FORMAT),
            'event': event,
        }
    return obj
