Credentials Load Testing
========================

This directory contains Locust tasks designed to exercise the `edX Credentials Service <https://github.com/edx/credentials>`_.

Getting Started
---------------

Load tests are configured using a YAML file. Refer to settings_files/credentials.yml.example for an example, then
create your own alongside it at `settings_files/credentials.yml`. Git will ignore this file, so you can put secrets in it.

Run the tests from the root of the ``edx-load-tests`` directory:

.. code-block:: bash

    # Loadtest
    $ locust --host=https://loadtest-edx-credentials.edx.org -f loadtests/credentials

    # Local
    $ locust --host=http://localhost:18150 -f loadtests/credentials
