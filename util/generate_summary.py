# -*- coding: utf-8 -*-
"""
Generate a summary of a previous loadtest run in this environment.

See for usage example in a jenkins job dsl:

https://github.com/edx/jenkins-job-dsl/blob/master/testeng/jobs/loadtestDriver.groovy

Prerequisites:
    A logfile produced by util/run-loadtest.sh should be present in its
    standard location.

Output:
    Produces summary on standard output in YAML format.  The structure is as
    follows:

    * monitoring_links:
        * list of link text/url pairs pointing to monitoring dashboards.
    * timeline:
        * begin: ISO 8601 date for when the test began.
        * end: ISO 8601 date for when the test ended.
"""
from datetime import timedelta
import yaml
import helpers.markers
from util.app_monitors_config import MONITORS

# Refer to util/run-loadtest.sh in case this file path changes.
STANDARD_LOGFILE_PATH = "results/log.txt"


def parse_logfile_events(logfile):
    """
    Parse the logfile for events

    Parameters:
        logfile (file): the file containing locust logs for a single load test

    Returns:
        iterator of (datetime.datetime, str) tuples: the parsed events in the
            order they are encountered.
    """
    for line in logfile:
        data = helpers.markers.parse_logfile_event_marker(line)
        if data is not None:
            yield (data['time'], data['event'])


def get_time_bounds(logfile):
    """
    Determine when the load test started and stopped.

    Parameters:
        logfile (file): the file containing locust logs for a single load test

    Returns:
        two-tuple of datetime.datetime: the time bounds of the load test
    """
    begin_time = end_time = None
    relevant_events = ['locust_start_hatching', 'edx_heartbeat', 'quitting']
    relevant_times = [
        time
        for time, event
        in parse_logfile_events(logfile)
        if event in relevant_events
    ]
    begin_time, end_time = (min(relevant_times), max(relevant_times))
    return (begin_time, end_time)


def main():
    """
    Generate a summary of a previous load test run.

    This script assumes "results/log.txt" is the logfile in question.
    """
    with open(STANDARD_LOGFILE_PATH) as logfile:
        loadtest_begin_time, loadtest_end_time = get_time_bounds(logfile)

    monitoring_links = []
    for monitor in MONITORS:
        monitoring_links.append({
            'url': monitor.url(
                begin_time=loadtest_begin_time,
                end_time=loadtest_end_time,
            ),
            'text': u'{}: {} ({} — {})'.format(
                monitor.monitoring_service_name,
                monitor.app_name,
                # We use naive datetimes (i.e. no attached tz) and just
                # assume UTC all along.  Tacking on the "Z" implies UTC.
                loadtest_begin_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                loadtest_end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            ),
        })
    print(yaml.dump(
        {
            'timeline': {
                'begin': loadtest_begin_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'end': loadtest_end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            },
            'monitoring_links': monitoring_links
        },
        default_flow_style=False,  # Represent objects using indented blocks
                                   # rather than inline enclosures.
        allow_unicode=True,
    ))

if __name__ == "__main__":
    main()
