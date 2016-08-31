edX Load Tests  |Travis|_
=========================
.. |Travis| image:: https://travis-ci.org/edx/edx-load-tests.svg?branch=master
.. _Travis: https://travis-ci.org/edx/edx-load-tests

This repository is home to public load tests for edX software components. New tests should be developed here. Old tests should be scrubbed and moved here over time.

Getting Started
---------------

If you have not already done so, create and activate a `virtualenv <https://virtualenvwrapper.readthedocs.org/en/latest/>`_. Unless otherwise stated, assume all commands below are executed within said virtualenv.

Next, install load testing requirements.

.. code-block::

    $ pip install -r requirements.txt

If the load test in question has additional requirements, install those too:

.. code-block::

    $ pip install -r loadtests/<test-name>/test-requirements.txt

Initialize and configure load test inputs.  This assumes the default
environment (loadtest):

.. code-block::

    $ paver settings --loadtest-name=<test-name>
    $ editor settings_files/<test-name>.yml

If you are targetting a sandbox or a devstack, try using the --environment
option:

.. code-block::

    $ paver settings --loadtest-name=<test-name> --environment=sandbox
    $ editor settings_files/<test-name>.yml

Start Locust by providing the Locust CLI with a target host and pointing it to
the location of your desired load test module:

.. code-block::

    $ locust --host=http://localhost:8009 -f loadtests/<test-name>

Repository Structure
--------------------

+------------------------------------+----------------------------------------------------+
| path                               | description                                        |
+====================================+====================================================+
| ``helpers/*``                      | *generally* helpful modules for writing load tests |
+------------------------------------+----------------------------------------------------+
| ``util/*``                         | standalone scripts and data                        |
+------------------------------------+----------------------------------------------------+
| ``loadtests/<test-name>/*``        | a load test module                                 |
+------------------------------------+----------------------------------------------------+
| ``settings_files/<test-name>.yml`` | settings for ``<test-name>``                       |
+------------------------------------+----------------------------------------------------+

Load test modules are organized under the top level ``loadtests`` directory. A
``locustfile.py`` is included inside each load test module, within which a
subclass of the `Locust class
<http://docs.locust.io/en/latest/writing-a-locustfile.html#the-locust-class>`_
is defined. This subclass is imported into the test package's ``__init__.py``
to facilitate discovery at runtime.  Settings for each test are read from
``settings_files/<testname>.yml``, and examples are provided.

Settings
--------

Test authors are responsible for creating the following YAML files:

* ``settings_files/<test-name>.yml.example``
* ``settings_files/<test-name>.yml.sandbox-example`` (optional)
* ``settings_files/<test-name>.yml.devstack-example`` (optional)

The first is the default and the most important.  It should be designed to work
with courses-loadtest.edx.org out of the box.  The other two should have sane
defaults for sandbox and devstack respectively.

To run a test, use paver to initialize the settings file for your test:

.. code-block::

    paver settings --loadtest-name=<test-name> [--environment=<environment>] [--force]

      --loadtest-name=<test-name>  the name of the loadtests to setup (REQUIRED)
      --environment=<environment>  the target environment for which to choose settings
      --force                      force the overwrite of pre-existing settings

This task will create the ``settings_files/<test-name>.yml`` necessary for
running <test-name>.  Secret keys may need to be provided, or you may want to
change the default settings---do so by editing this file.  All
``settings_files/*.yml`` files are ignored by ``.gitignore`` in order to
protect secrets.

License
-------

The code in this repository is licensed under the Apache License, Version 2.0, unless otherwise noted.

Please see `LICENSE.txt <https://github.com/edx/edx-load-tests/blob/master/LICENSE.txt>`_ for details.

How To Contribute
-----------------

Contributions are very welcome.

Please read `How To Contribute <https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst>`_ for details.

Even though they were written with ``edx-platform`` in mind, the guidelines
should be followed for Open edX code in general.

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org.

Mailing List and Slack Channel
----------------------------

You can discuss this code in the `edx-code Google Group` or in the ``#general`` slack channel.

* https://groups.google.com/forum/#!forum/edx-code
* http://openedx-slack-invite.herokuapp.com/
