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

    $ make requirements

If the load test in question has additional requirements, install those too:

.. code-block::

    $ pip install -r <test-name>/requirements.txt (consult the <test-name> directory)

Configure load test inputs. For example:

.. code-block::

    $ cp settings_files/<test-name>.yml.example settings_files/<test-name>.yml
    $ editor settings_files/<test-name>.yml

Start Locust by a target host and the name of your test. For example,

.. code-block::

    $ HOST=http://localhost:8009 make <test-name>

You can also provide extra arguments by invoking locust directly:

.. code-block::

    $ locust --host=http://localhost:8009 -f <test-name> --no-web --clients=20 --hatch-rate=2

Repository Structure
--------------------

Tests are organized into top-level packages. For examples, see ``csm`` or ``enrollment``. A module called ``locustfile.py`` is included inside each test package, within which a subclass of the `Locust class <http://docs.locust.io/en/latest/writing-a-locustfile.html#the-locust-class>`_ is defined. This subclass is imported into the test package's ``__init__.py`` to facilitate discovery at runtime.  Settings for each test are read from ``settings_files/<testname>.yml``, and examples are provided.

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

Mailing List and IRC Channel
----------------------------

You can discuss this code in the `edx-code Google Group` or in the ``#general`` slack channel.

* https://groups.google.com/forum/#!forum/edx-code
* http://openedx-slack-invite.herokuapp.com/
