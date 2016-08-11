E-Commerce Load Testing
=======================

This directory contains Locust tasks designed to exercise ecommerce
behavior on the LMS and the E-Commerce Service (also known as Otto).
Currently, access to Otto is always through the LMS. If a user tries to
enroll in a course on the LMS, the LMS makes a call to Otto which is
responsible for creating and coordinating fulfillment of an order for
the corresponding product, ultimately resulting in an enrollment.

Getting Started
---------------

In order to run the tests, auto auth must be enabled on the LMS. In
addition, courses to be used for testing must be configured on both the
LMS and Otto. At a minimum, these load tests require the existence of
two courses on the LMS instance being used for testing. The edX
Demonstration Course should be present by default on most LMS instances.
Use Studio to create a course. Use Otto’s "Course Administration Tool"
(CAT) to finish configuring the courses you created above. When
developing, you can find the CAT at ``http://localhost:8002/courses/``.
Add both of the courses present on your LMS instance to Otto. Configure
one as a "Free (Honor)" course, and the second as a "Verified" course.

Configuration
-------------

FIXME: this load test does not yet implement the settings interface in
helpers/settings.py.

The load tests rely on configuration which can be specified using
environment variables.

+--------------------------+-----------+------------------------------------------------------------+
| Variables                | Required? | Description                                                |
+==========================+===========+============================================================+
| FREE_COURSE_ID           | No        | ID of a course with a free course seat                     |
+--------------------------+-----------+------------------------------------------------------------+
| PAID_SKU                 | Yes       | SKU corresponding to a paid course seat                    |
+--------------------------+-----------+------------------------------------------------------------+
| ECOMMERCE_SERVICE_URL    | No        | URL root for the ecommerce service                         |
+--------------------------+-----------+------------------------------------------------------------+
| ECOMMERCE_JWT_SECRET     | No        | Key to use when signing JWTs sent to the ecommerce service |
+--------------------------+-----------+------------------------------------------------------------+
| ECOMMERCE_JWT_ISSUER     | No        | String used to identify an app issuing JWTs                |
+--------------------------+-----------+------------------------------------------------------------+
| CYBERSOURCE_SECRET_KEY   | No        | Key to use when signing CyberSource transaction parameters |
+--------------------------+-----------+------------------------------------------------------------+
| BASIC_AUTH_USER          | No        | Username to use for basic access authentication            |
+--------------------------+-----------+------------------------------------------------------------+
| BASIC_AUTH_PASSWORD      | No        | Password to use for basic access authentication            |
+--------------------------+-----------+------------------------------------------------------------+
| LOCUST_TASK_SET          | No        | TaskSet to run; must be imported into the locustfile       |
+--------------------------+-----------+------------------------------------------------------------+

If you want to use the defaults provided for these variables - in
particular, ``ECOMMERCE_JWT_SECRET_KEY`` and ``CYBERSOURCE_SECRET_KEY``
- make sure that these defaults are configured across both the LMS and
Otto.

Running
-------

You can run the E-Commerce load tests from the top level ``edx-load-tests`` directory by executing something like the following:

.. code-block:: bash

    $ FREE_COURSE_ID=<course_id> PAID_SKU=<sku> locust -f ecommerce --host=http://localhost:8000

There appears to be a bug in Locust preventing tests from accessing hosts using SSL.
To get around this, use `http` as the protocol in the host URL, not `https`.
