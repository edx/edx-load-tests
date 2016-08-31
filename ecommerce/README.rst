E-Commerce Load Testing
=======================

This directory contains Locust tasks designed to exercise ecommerce behavior on the LMS and the E-Commerce Service (also known as Otto). Currently, access to Otto is always through the LMS. If a user tries to enroll in a course on the LMS, the LMS makes a call to Otto which is responsible for creating and coordinating fulfillment of an order for the corresponding product, ultimately resulting in an enrollment.

Getting Started
---------------

Load tests are configured using a YAML file. Refer to settings_files/ecommerce.yml.example for an example, then create your own alongside it at settings_files/ecommerce.yml. Git will ignore this file, so you can put secrets in it.

In order to run the tests, auto auth must be enabled on the LMS. In addition, courses to be used for testing must be configured on both the LMS and Otto. At a minimum, these load tests require the existence of two courses on the LMS instance being used for testing. The edX Demonstration Course should be present by default on most LMS instances. Use Studio to create a course. Use Otto’s "Course Administration Tool" (CAT) to finish configuring the courses you created above. When developing, you can find the CAT at ``http://localhost:8002/courses/``. Add both of the courses present on your LMS instance to Otto. Configure one as a "Free (Honor)" course, and the second as a "Verified" course.

Running
-------

You can run the E-Commerce load tests from the top level ``edx-load-tests`` directory by executing something like the following:

.. code-block:: bash

    $ locust --host=https://localhost:8000 -f ecommerce
