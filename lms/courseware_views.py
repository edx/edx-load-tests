from locust import task

from lms import LmsTasks


class CoursewareViewsTasks(LmsTasks):
    """
    Please don't actually merge this change
    We just want some baseline data about the progress page, so everything else in this file is getting chopped

    The stuff that was here before is still generally useful, so it ought to stay on master.

    /courseware.views:progress              331582     4.00%
    """

    @task
    def progress(self):
        """
        Request the progress tab.
        """
        self.get('progress', name='courseware:progress')
