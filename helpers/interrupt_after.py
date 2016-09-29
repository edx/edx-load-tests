"""
This file defines the interrupt_after decorator for locusts tasks.

If your load test only has one TaskSet, ignore this utility.  Else, read on...

Normally the locust client gets captured by a TaskSet class, preventing it from
escaping to run tasks in sibling TaskSet classes unless it explicitly runs a
task which calls the interrupt() function.  This interrupt_after decorator is
simply a tool for calling the interrupt() function safely.

If it is not detrimental to the load test results to have locust users hopping
between TaskSets, you should consider using the interrupt_after decorator on
all tasks of all TaskSets in your load test.  For small numbers of locust
clients (especially when the test target is a load balancer) this will
generally help keep the transaction distribution even.
"""


def is_root(task_set):
    """
    Return True if task_set is a root TaskSet instance, which means that it has
    been called directly from the Locust class and so it has no parent.
    """
    # use `is` instead of `==` for reference equality
    return task_set.parent is task_set.locust


def interrupt_after(func):
    """
    Decorator for a locust task which causes it to be the last task to be
    scheduled in the current TaskSet, unless the current TaskSet is the root
    TaskSet---in the latter case this decorator is a no-op.

    Use after the @task decorator:

        @task(21)
        @interrupt_after
        def some_task(self): ...

    """
    def _interrupt_after(self, *args, **kwargs):
        func(self, *args, **kwargs)
        # Before interrupting, make sure that there is a parent task set to
        # escape to.  Otherwise locust will crash.
        if not is_root(self):
            self.interrupt()

    return _interrupt_after
