Ecommerce Loadtests for Performance related issues
==================================================

These ecommerce load tests are designed to mimic issues we have seen in ecommerce production.

The goal is to reproduce deadlock time outs and other django transaction issues.

Getting Started
---------------

#. Create a python3 virtual env.
#. Install the requirements. Use the requirements file in the `ecommerce_deadlock` folder.
#. Set up settings file. Use ``ecommerce_deadlock.yml.example`` as an example.
#. Set up the temporary constants file. Use ``ecommerce_deadlock_constants.py.example`` as an example.
#. Navigate to the folder that has this loadtest folder. You should be in the folder ``loadtests``.
#. Run locust and visit localhost:8089 to use their web GUI.

  .. code-block:: bash

      $ locust -f ecommerce_deadlock/locustfile.py
