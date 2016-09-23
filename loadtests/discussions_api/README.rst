Discussion API Load Tests
=========================

This document explains how to run load tests against the Discussion API.


Prepping Environment
--------------------

If you haven't set up locust in general, follow instructions for setting up
locust and a virtual env in edx-load-tests/README.rst.

Once locust is set up, configure and start your environment as follows:

#. Set AUTOMATIC_AUTH_FOR_TESTING to true in ``/edx/app/edxapp/lms.env.json``. (for load testing)
#. Verify mongo indexes (see below).
#. Start up Studio (for seeding).
#. Start up LMS.
#. Start up forums comment service.

Verify Mongo Indexes
~~~~~~~~~~~~~~~~~~~~

For now, the indexes probably don't exist on your devstack or a sandbox.

First, you'll need to copy the create index script from edx-load-tests/discussions_api/db/create_indexes.js to cs_comments_service/scripts/db/create_indexes.js.

Next, from the mongo shell, you can run the following to see what indexes exist::

    > show dbs
    > use cs_comments_service_development
    > db.contents.getIndexes()

After the above setup, you can run the following script from the mongo shell to ensure the indexes have all been created::

    > load("/edx/app/forum/cs_comments_service/scripts/db/create_indexes.js")

Seeding Data
------------

Before running load tests, you will need to seed your database with test data.

.. code-block:: bash

    # Run the seed script from the edx-load-tests directory.
    $ cd edx-load-tests

    # For help, use -h
    $ python discussions_api/seed_data/seed_data.py -h


Seeding Test Course
~~~~~~~~~~~~~~~~~~~

You can either supply a course id to the scripts (see below), or a course will
automatically be created for you.


Seeding Comments and Threads
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following give an example of creating some threads, comments and responses.

.. code-block:: bash

    # Run this from the edx-load-tests directory.
    $ cd edx-load-tests

    # Here is an example that will create threads, responses and comments:
    $ python discussions_api/seed_data/seed_data.py -c course-v1:testX+C1+2016_C1 -s http://localhost:8001 -l http://localhost:8000 -e staff@example.com -p edx -a GetCommentsTasks -t 1 -r 2 -m 3


Running Load Test
-----------------

#. Update `settings_files/discussions_api.yml` with the provided COURSE_ID and
   SEEDED_DATA output from seed_data.py script
#. Run tests with something like:

.. code-block:: bash

    $ locust -f discussions_api -c 2 -r 10 -n 200 -H http://localhost:8000 --no-web


Troubleshooting
---------------

If you see any authorization or other errors, you can `follow instructions in
the wiki <https://openedx.atlassian.net/wiki/display/EdxOps/How+to+Run+Performance+Tests>`_.

If you are getting CSRF Token errors that are not covered above, be sure to
include settings variables BASIC_AUTH_USER BASIC_AUTH_PASSWORD if you
are running against a protected sandbox.

If you are getting 500 errors, check that the comment service is up and running
and the Discussions tab is working through the browser.
