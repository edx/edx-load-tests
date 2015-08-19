"""
Generate graphs from the raw Locust data captured in MongoDB.

You must have installed the requirements in the util_requirements.txt file in order to
successfully run this script.
"""

import datetime
import click
import pymongo
# If you remove the pandas import below, some of the numpy calls fail below.
# TODO: Figure out why...
import pandas as pd
import numpy as np

from bokeh.plotting import figure as bokeh_figure, output_file as bokeh_output_file, show as bokeh_show
from bokeh.embed import components as bokeh_components
from mako.template import Template

# MongoDB defaults
DEFAULT_MONGO_HOST = "localhost"
DEFAULT_MONGO_PORT = 27017
DEFAULT_MONGO_DATABASE = "locust_data"

RAW_DATA_COLLECTION_FMT = 'requests_{}'
TEST_RUN_COLLECTION = "test_runs"


class MongoConnection(object):
    """
    Base class for connecting to MongoDB.
    """
    def __init__(self, db, host, port=27107, tz_aware=True, user=None, password=None, **kwargs):
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


def scatter_plot(successes, failures, label):
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
    min_time = all_success_timestamps[0]
    max_time = all_success_timestamps[-1]
    num_bins = 1 + (max_time - min_time) / bin_interval

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
    max_per_interval = [ max(x) if len(x) else 0 for x in vals_per_interval ]

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
    p = bokeh_figure(
        title=label,
        tools=TOOLS,
        x_range=(min_time, max_time),
        y_range=(0, y_max)
    )
    p.xaxis.axis_label = "Time"
    p.yaxis.axis_label = "Mean Response Time (ms)"

    # Scatter-plot the mean response time data for successes.
    p.circle(x=np.array(time_bins), y=means_per_interval, fill_color='blue')

    # Scatter-plot the failure response times for all failures.
    p.x(x=np.array(failure_timestamps), y=failure_resp_times, line_color='red')

    return p


def get_all_request_types(collection):
    """
    Returns a dict with request types as keys and values, in order to have a
    special None value for all requests.
    """
    all_names = collection.distinct("name")
    all = dict(zip(all_names, all_names))
    all['All Requests'] = None
    return all


def output_report(ctx, test_run):
    """
    Output a report analyzing a test run.
    """
    conn = MongoConnection(
        host=ctx.obj['MONGO_HOST'],
        port=ctx.obj['MONGO_PORT'],
        db=ctx.obj['MONGO_DBNAME']
    )
    resp_collection = conn.database[RAW_DATA_COLLECTION_FMT.format(test_run)]
    req_types = get_all_request_types(resp_collection)

    # Grab all the Locust-generated data.
    run_collection = conn.database[TEST_RUN_COLLECTION]
    run_data = run_collection.find_one({'_id': test_run})

    # Generate plots for each request type.
    all_plots = {}
    for label, req_query in req_types.iteritems():
        req_data = get_req_data(resp_collection, label, req_query)
        if len(req_data[0]) == 0:
            # No successes to plot.
            continue
        p = scatter_plot(*req_data, label=label)
        all_plots[label] = p

    # Output an HTML report of the test run.
    script, divs = bokeh_components(all_plots)

    from mako import exceptions

    with open('report.html', 'w') as outfile:
        try:
            report_template = Template(filename='static/test_run_report.html')
            outfile.write(report_template.render(
                script=script,
                divs=divs,
                run_title='CSM Load Test Run: {}'.format(test_run),
                run_data=run_data
            ))
        except:
            outfile.write(exceptions.html_error_template().render())


def get_req_data(collection, label, req_type):
    """
    Read test run data from MongoDB.
    """
    print "Reading data for '{}'...".format(label)

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


def get_test_runs(ctx):
    """
    Get all test run IDs.
    """
    db = MongoConnection(
        host=ctx.obj['MONGO_HOST'],
        port=ctx.obj['MONGO_PORT'],
        db=ctx.obj['MONGO_DBNAME']
    )
    test_runs = db.database[TEST_RUN_COLLECTION]
    return [run_id['_id'] for run_id in test_runs.find(projection=['_id'], sort=[('_id', pymongo.ASCENDING)])]


def print_test_runs(ctx):
    """
    Print all test run IDs.
    """
    for run_id in get_test_runs(ctx):
        click.echo(run_id)


@click.group()
@click.option('--mongo_host',
              default=DEFAULT_MONGO_HOST,
              help="MongoDB host name to connect to.",
              required=False
              )
@click.option('--mongo_port',
              default=DEFAULT_MONGO_PORT,
              help="MongoDB port to connect to.",
              required=False
              )
@click.option('--mongo_dbname',
              default=DEFAULT_MONGO_DATABASE,
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
def analyze(ctx, test_run):
    """
    Generate graphs for a CSM load test run using the raw data captured in MongoDB.
    """
    if test_run is None:
        # If no test run is specified, use the latest test run.
        test_run = get_test_runs(ctx)[-1]
    output_report(ctx, test_run)



if __name__ == '__main__':
    cli(obj={})  # pylint: disable=no-value-for-parameter
