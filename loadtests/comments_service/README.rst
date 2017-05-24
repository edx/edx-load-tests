**********************
comments_service tests
**********************

Getting Data
------------

The comments_service load tests rely on knowing what data to request
from the comments_service.  In order to get fresh data, run the mongo
scripts in the :code:`scripts/` directory on the mongo environment
being tested.  Save the output as JSON then run the load test with the
:code:`USERS_FILE`, :code:`COMMENTABLES_FILE`, :code:`THREADS_FILE`,
and :code:`COURSES_FILE` environment variables pointing to the
appropriate JSON files.
