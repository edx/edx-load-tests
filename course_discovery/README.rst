Course Discovery Load Tests
===========================

This directory contains Locust tasks designed to exercise the `edX catalog service <https://github.com/edx/course-discovery>`_, also referred to as the course discovery service.

Getting Started
---------------

Load tests are configured using a YAML file. Refer to settings_files/course_discovery.yml.example for an example, then create your own alongside it at settings_files/course_discovery.yml. Git will ignore this file, so you can put secrets in it.

Run the tests from the root of the ``edx-load-tests`` directory by defining your target ``HOST`` and using the provided Make target:

.. code-block:: bash

    $ HOST=https://loadtest-edx-discovery.edx.org/ make course_discovery
