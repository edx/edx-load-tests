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
import matplotlib.pyplot as plt

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


def scatter_plot(successes, failures):
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

    # FAILURES
    # Convert all failure response timestamps to numpy datetimes.
    all_failure_timestamps = np.array(
        [np.datetime64(datetime.datetime.isoformat(s['timestamp'])) for s in failures]
    )
    all_failure_timestamps_i8 = all_failure_timestamps.view('i8')

    # Convert each failure response time into a plottable point against its time bin.
    binned = np.digitize(all_failure_timestamps_i8, time_bins_i8)
    failure_timestamps = []
    failure_resp_times = []
    for i, n in enumerate(binned):
        failure_timestamps.append(time_bins[n - 1])
        failure_resp_times.append(failures[i]['response_time'])

    # Set axes labels and limits.
    plt.xlabel("Time")
    plt.ylabel("Mean Response Time (ms)")
    plt.xlim(min_time, max_time)

    # Scatter-plot the mean response time data for successes.
    plt.scatter(np.array(time_bins), means_per_interval)

    # Scatter-plot the failure response times for all failures.
    plt.scatter(np.array(failure_timestamps), failure_resp_times, marker='x', c='red')

    plt.show()


def read_req_data(mongo_host, mongo_port, db, collection):
    """
    Read all test run data from MongoDB.
    For now, assume that all data in the DB should be graphed.
    """
    print "Reading data..."
    db = MongoConnection(db=db, host=mongo_host, port=mongo_port)
    req_data = db.database[collection]
    successes = [
        successful_req for successful_req in req_data.find({"result": "success"}).sort("timestamp", pymongo.ASCENDING)
    ]
    print "Success read complete ({}).".format(len(successes))
    failures = [
        failed_req for failed_req in req_data.find({"result": "failure"}).sort("timestamp", pymongo.ASCENDING)
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

    req_data = read_req_data(
        ctx.obj['MONGO_HOST'],
        ctx.obj['MONGO_PORT'],
        ctx.obj['MONGO_DBNAME'],
        RAW_DATA_COLLECTION_FMT.format(test_run)
    )
    scatter_plot(*req_data)


if __name__ == '__main__':
    cli(obj={})  # pylint: disable=no-value-for-parameter
