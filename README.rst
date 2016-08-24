edX Load Tests  |Travis|_
=========================
.. |Travis| image:: https://travis-ci.org/edx/edx-load-tests.svg?branch=master
.. _Travis: https://travis-ci.org/edx/edx-load-tests

This repository is home to public load tests for edX software components. New tests should be developed here. Old tests should be scrubbed and moved here over time.

Getting Started
---------------

If you have not already done so, create and activate a `virtualenv <https://virtualenvwrapper.readthedocs.org/en/latest/>`_. Unless otherwise stated, assume all commands below are executed within said virtualenv.

Prepare a load test using its make target.  This should install pip
dependencies and a settings file. For example:

.. code-block::

    $ make <test-name>

If you are testing against a specific environment, such as devstack:

.. code-block::

    $ LT_ENV=devstack make <test-name>

Optionally modify the settings:

.. code-block::

    $ editor settings_files/<test-name>.yml

Start Locust by supplying a target host and pointing it to the location of your
desired load test module:

.. code-block::

    $ locust --host=http://localhost:8009 -f loadtests/<test-name>

Repository Structure
--------------------

+--------------------------------------------+----------------------------------------------------+
| path                                       | description                                        |
+============================================+====================================================+
| ``helpers/*``                              | *generally* helpful modules for writing load tests |
+--------------------------------------------+----------------------------------------------------+
| ``util/*``                                 | standalone scripts and data                        |
+--------------------------------------------+----------------------------------------------------+
| ``loadtests/<test-name>/*``                | a load test module                                 |
+--------------------------------------------+----------------------------------------------------+
| ``loadtests/<test-name>/__init__.py``      | contains code which exposes a Locust subclass      |
+--------------------------------------------+----------------------------------------------------+
| ``loadtests/<test-name>/requirements.txt`` | all pip requirements for running this load test    |
+--------------------------------------------+----------------------------------------------------+
| ``settings_files/<test-name>.yml``         | settings for ``<test-name>``                       |
+--------------------------------------------+----------------------------------------------------+

Load test modules are organized under the top level ``loadtests`` directory. A
``locustfile.py`` is included inside each load test module, within which a
subclass of the `Locust class
<http://docs.locust.io/en/latest/writing-a-locustfile.html#the-locust-class>`_
is defined. This subclass is imported into the test package's ``__init__.py``
to facilitate discovery at runtime.  Settings for each test are read from
``settings_files/<testname>.yml``, and examples are provided.

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
