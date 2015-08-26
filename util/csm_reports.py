"""
Generate graphs from the raw Locust data captured in MongoDB.

You must have installed the requirements in the util_requirements.txt file in order to
successfully run this script.
"""

import os
import sys
import datetime
import click
import pymongo
import numpy as np
import itertools
import heapq

from bokeh.plotting import figure as bokeh_figure, output_file as bokeh_output_file, show as bokeh_show
from bokeh.embed import components as bokeh_components
from csv import DictReader
from collections import defaultdict
from mako.lookup import TemplateLookup
import mako.exceptions

from helpers.mongo_connection import RawDataCollection, MongoConnection


TEMPLATE_LOOKUP = TemplateLookup(
    directories=[
        os.path.join(os.path.dirname(__file__), 'static')
    ]
)


def scatter_plot(successes, failures, label, min_time=None, max_time=None):
    """
    Scatter plot the successes/failures for a particular request type.
    """
    # Make time bins at this regular time interval.
    bin_interval = np.timedelta64(1, 'm')

    # SUCCESSES
    # Convert all success response timestamps to numpy datetimes.
    all_success_timestamps = np.array(
        [np.datetime64(datetime.datetime.isoformat(s['timestamp'])) for s in successes]
    )

    # Start the bins with the initial response time.
    min_time, max_time = [np.datetime64(datetime.datetime.isoformat(x)) for x in [min_time, max_time]]
    num_bins = 50 #1 + (max_time - min_time) / bin_interval
    bin_interval = (max_time - min_time) / num_bins

    # Make regular time-intervaled bins until all response times are covered.
    time_bins = []
    for i in range(int(num_bins)):
        time_bins.append(min_time + bin_interval * i)

    # Convert the timestamps into a comparable data type.
    all_success_timestamps_i8 = all_success_timestamps.view('i8')
    time_bins_i8 = np.array(time_bins).view('i8')

    # Aggregate each response time into the appropriate time bin.
    binned = np.digitize(all_success_timestamps_i8, time_bins_i8)
    vals_per_interval = [[] for x in xrange(time_bins_i8.size)]
    for i, n in enumerate(binned):
        vals_per_interval[n - 1].append(successes[i]['response_time'])

    # Calculate the mean for each time bin.
    means_per_interval = [np.mean(x) if len(x) else 0.0 for x in vals_per_interval]

    # Extract the max response time per interval.
    max_per_interval = [max(x) if len(x) else 0 for x in vals_per_interval]

    # FAILURES
    # Convert all failure response timestamps to numpy datetimes.
    all_failure_timestamps = np.array(
        [np.datetime64(datetime.datetime.isoformat(s['timestamp'])) for s in failures]
    )
    all_failure_timestamps_i8 = all_failure_timestamps.view('i8')

    # Convert each failure response time into a plottable point against its time bin.
    binned = []
    if len(all_failure_timestamps_i8):
        binned = np.digitize(all_failure_timestamps_i8, time_bins_i8)
    failure_timestamps = []
    failure_resp_times = []
    for i, n in enumerate(binned):
        failure_timestamps.append(time_bins[n - 1])
        failure_resp_times.append(failures[i]['response_time'])

    TOOLS = "resize,crosshair,pan,wheel_zoom,box_zoom,reset,box_select"

    # Find the maximum y-value.
    y_max = max(max_per_interval)
    if len(failure_resp_times):
        y_max = max(y_max, max(failure_resp_times))

    # Create a new plot with the tools above, and set axis labels.
    graph_plot = bokeh_figure(
        title=label,
        tools=TOOLS,
        x_range=(min_time, max_time),
        y_range=(0, y_max)
    )
    graph_plot.xaxis.axis_label = "Time"
    graph_plot.yaxis.axis_label = "Mean Response Time (ms)"

    # Scatter-plot the mean response time data for successes.
    graph_plot.circle(x=np.array(time_bins), y=means_per_interval, fill_color='blue')

    # Scatter-plot the failure response times for all failures.
    graph_plot.x(x=np.array(failure_timestamps), y=failure_resp_times, line_color='red')

    return graph_plot


def _connect_to_mongo(ctx):
    """
    Utility function to connect to MongoDB.
    """
    return MongoConnection(
        host=ctx.obj['MONGO_HOST'],
        port=ctx.obj['MONGO_PORT'],
        db=ctx.obj['MONGO_DBNAME']
    )


def output_report(data_source):
    """
    Output a report analyzing a test run.
    """
    all_plots = []
    min_time = None
    max_time = None

    # Generate a single plot for all requests.
    (successes, failures) = data_source.get_req_data(None)
    mins = []
    maxes = []

    if successes:
        mins.append(successes[0]['timestamp'])
        maxes.append(successes[-1]['timestamp'])

    if failures:
        mins.append(failures[0]['timestamp'])
        maxes.append(failures[-1]['timestamp'])
        
    # Set minimum and maximum times from all request data.
    min_time = min(mins)
    max_time = max(maxes)
    all_plots.append(scatter_plot(
        successes, failures, label='All Requests', min_time=min_time, max_time=max_time
    ))

    # Generate a plot for each request type.
    for req_type in data_source.req_types:
        (successes, failures) = data_source.get_req_data(req_type)
        if len(successes):
            all_plots.append(scatter_plot(
                successes, failures, label=req_type, min_time=min_time, max_time=max_time
            ))

    # Output an HTML report of the test run.
    script, divs = bokeh_components(all_plots)

    with open('report.html', 'w') as outfile:
        try:
            report_template = TEMPLATE_LOOKUP.get_template('test_run_report.html')
            outfile.write(report_template.render(
                script=script,
                divs=divs,
                run_title='CSM Load Test Run: {}'.format(data_source.test_run),
                run_data=data_source.run_data
            ))
        except:
            outfile.write(mako.exceptions.html_error_template().render())


class DataSource(object):
    def get_req_data(req_type):
        """
        Return a tuple of (successes, failures) requests for the specified req_type
        """
        raise NotImplementedError()


class MongoDataSource(DataSource):
    def __init__(self, ctx, test_run):
        conn = _connect_to_mongo(ctx)
        self.resp_collection = conn.database[RawDataCollection.RAW_DATA_COLLECTION_FMT.format(test_run)]
        req_types = sorted(self.resp_collection.distinct("name"))

        # Grab all the Locust-generated data.
        self.run_collection = conn.database[RawDataCollection.TEST_RUN_COLLECTION]
        self.run_data = self.run_collection.find_one({'_id': test_run})


    def get_req_data(self, req_type):
        """
        Read test run data from MongoDB.
        """
        if req_type:
            print "Reading data for '{}'...".format(req_type)
        else:
            print "Reading all data ..."

        query = {'name': req_type} if req_type else {}

        query['result'] = 'success'
        successes = [
            successful_req for successful_req in collection.find(query).sort("timestamp", pymongo.ASCENDING)
        ]
        print "Success read complete ({}).".format(len(successes))

        query['result'] = 'failure'
        failures = [
            failed_req for failed_req in collection.find(query).sort("timestamp", pymongo.ASCENDING)
        ]
        print "Failure read complete ({}).".format(len(failures))

        return (successes, failures)


class FileDataSource(DataSource):

    def __init__(self, files):
        self.files = files
        self.test_run = self.files[0].name
        self.run_data = None

        data = itertools.chain.from_iterable(DictReader(file) for file in self.files)

        self.data_by_type = defaultdict(lambda: ([], []))
        for request in data:
            request['start_time'] = datetime.datetime.fromtimestamp(float(request['start_time']))
            request['end_time'] = datetime.datetime.fromtimestamp(float(request['end_time']))
            request['response_time'] = float(request['response_time'])
            request['response_length'] = int(request['response_length'])
            request['timestamp'] = request['start_time']
            if request['result'] == 'success':
                self.data_by_type[request['name']][0].append(request)
            else:
                self.data_by_type[request['name']][1].append(request)

        for requests in self.data_by_type.values():
            requests[0].sort()
            requests[1].sort()

    @property
    def req_types(self):
        return self.data_by_type.keys()

    def get_req_data(self, req_type):
        if req_type is None:
            successes = [successes for (successes, _) in self.data_by_type.values()]
            failures = [failures for (_, failures) in self.data_by_type.values()]
            return (
                list(heapq.merge(*successes)),
                list(heapq.merge(*failures)),
            )

        return self.data_by_type[req_type]


def get_test_runs(ctx):
    """
    Get all test run IDs.
    """
    db = _connect_to_mongo(ctx)
    test_runs = db.database[RawDataCollection.TEST_RUN_COLLECTION]
    return [run_id['_id'] for run_id in test_runs.find(projection=['_id'], sort=[('_id', pymongo.ASCENDING)])]


def print_test_runs(ctx):
    """
    Print all test run IDs.
    """
    for run_id in get_test_runs(ctx):
        click.echo(run_id)


@click.group()
@click.option('--mongo_host',
              default="localhost",
              help="MongoDB host name to connect to.",
              required=False
              )
@click.option('--mongo_port',
              default=27017,
              help="MongoDB port to connect to.",
              required=False
              )
@click.option('--mongo_dbname',
              default=RawDataCollection.MONGO_DATABASE_NAME,
              help="MongoDB database to use.",
              required=False
              )
@click.pass_context
def cli(ctx, mongo_host, mongo_port, mongo_dbname):
    """
    Script used to analyze data from CSM Locust tests.
    """
    ctx.obj['MONGO_HOST'] = mongo_host
    ctx.obj['MONGO_PORT'] = mongo_port
    ctx.obj['MONGO_DBNAME'] = mongo_dbname


@cli.command()
@click.pass_context
def print_runs(ctx):
    """
    Prints all test run ids.
    """
    print_test_runs(ctx)


@cli.command()
@click.option('--test_run',
              default=None,
              help="Test run id to analyze (YYYYMMDD_HHMMSS).",
              required=False
              )
@click.pass_context
def analyze_mongo(ctx, test_run):
    """
    Generate graphs for a CSM load test run using the raw data captured in MongoDB.
    """
    if test_run is None:
        # If no test run is specified, use the latest test run.
        test_run = get_test_runs(ctx)[-1]
    data_source = MongoDataSource(ctx, test_run)
    output_report(data_source)


@cli.command()
@click.argument(
    'files',
    type=click.File('r'),
    nargs=-1,
    required=False,
)
def analyze_files(files):
    output_report(FileDataSource(files))

if __name__ == '__main__':
    cli(obj={})  # pylint: disable=no-value-for-parameter
