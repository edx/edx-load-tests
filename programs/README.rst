Programs Load Testing
=====================

WARNING: the programs service is officially being retired as of 2016-08-02.

This directory contains Locust tasks designed to exercise the `edX Programs Service <https://github.com/edx/programs>`_.

Getting Started
---------------

At this point, these load tests only require a running instance of the Programs service.

Configuration
-------------

The load tests rely on configuration which can be specified using environment variables.

==================== ========= ===========================================
Variable             Required? Description
==================== ========= ===========================================
PROGRAMS_SERVICE_URL No        URL root for the Programs service
PROGRAMS_API_URL     No        URL root for the Programs API
JWT_AUDIENCE         No        JWT audience claim (aud)
JWT_ISSUER           No        JWT issuer claim (iss)
JWT_EXPIRATION_DELTA No        Number of days before generated JWTs expire
JWT_SECRET_KEY       Yes       Secret key used to sign JWTs
==================== ========= ===========================================

If you want to use the defaults provided for these variables, make sure that these defaults are configured for your instance of the Programs service.

Running
-------

You can run the Programs load tests from the top level ``edx-load-tests`` directory by executing something like the following:

.. code-block:: bash

    $ JWT_SECRET_KEY=replace-me locust --host=http://localhost:8009/ -f programs

As of this writing, there is a bug in Locust preventing tests from accessing hosts using SSL. This is attributable to an `issue with gevent <https://github.com/gevent/gevent/issues/477>`_ that appears to have been fixed in 1.0.2. However, Locust still `requires <https://github.com/locustio/locust/blob/master/setup.py#L50>`_ the broken 1.0.1. To get around this, use ``http`` as the protocol in the host URL, not ``https``.
