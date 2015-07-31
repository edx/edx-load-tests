This project is the single source for public load tests for edX software component.  New tests should be developed here unless there is a very good reason why that cannot be the case.  Old tests should be scrubbed and moved here over time.


Installation
------------

mkvirtualenv edx-load-tests
pip install -r locust/requirements.txt
cd locust/$TEST_DIR
locust --host="http://localhost"

License
-------

The code in this repository is licensed under version 3 of the AGPL
unless otherwise noted. Please see the `LICENSE`_ file for details.

.. _LICENSE: https://github.com/edx/edx-load-tests/blob/master/LICENSE

