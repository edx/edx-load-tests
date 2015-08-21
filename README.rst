This project is the single source for public load tests for edX software component.  New tests should be developed here unless there is a very good reason why that cannot be the case.  Old tests should be scrubbed and moved here over time.


Installation
------------

mkvirtualenv edx-load-tests
pip install -r locust/requirements.txt
cd locust/$TEST_DIR
locust --host="http://localhost" -f $csm

Layout
------

Each set of tasks should be captured as a top-level locustfile named
for the particular set of endpoints being tested. This toplevel file
can be a flat python file (lms.py) or a directory (csm/). In the case
of a directory, the __init__.py file should have (or import) the Locust
subclass that defines the test.

License
-------

The code in this repository is licensed under version 3 of the AGPL
unless otherwise noted. Please see the `LICENSE`_ file for details.

.. _LICENSE: https://github.com/edx/edx-load-tests/blob/master/LICENSE

