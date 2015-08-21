"""
Code which provides a MongoDB connection.
"""

import pymongo

# MongoDB defaults
DEFAULT_MONGO_HOST = "localhost"
DEFAULT_MONGO_PORT = 27017


class RawDataCollection(object):
    """
    Constants specific to Locust raw data collection.
    """
    # Store all the locust data in this database.
    MONGO_DATABASE_NAME = 'locust_data'

    # Final collection name for data at the end of a test run.
    RAW_DATA_COLLECTION_FMT = 'requests_{}'

    # Mongo collection that contains data about each test run.
    TEST_RUN_COLLECTION = 'test_runs'


class MongoConnection(object):
    """
    Base class for connecting to MongoDB.
    """
    def __init__(self, db, host=DEFAULT_MONGO_HOST, port=DEFAULT_MONGO_PORT, tz_aware=True, user=None, password=None, **kwargs):
        """
        Create & open the connection - and authenticate.
        """
        self.database = pymongo.database.Database(
            pymongo.MongoClient(
                host=host,
                port=port,
                tz_aware=tz_aware,
                w=0,
                **kwargs
            ),
            db
        )

        if user is not None and password is not None:
            self.database.authenticate(user, password)

