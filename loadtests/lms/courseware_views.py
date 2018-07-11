from locust import task

from base import LmsTasks


class CoursewareViewsTasks(LmsTasks):
    """
    Models traffic for endpoints in lms.djangoapps.courseware.views

    Traffic Distribution on courses.edx.org (last 7d as of 2014-02-24):

    /courseware.views:course_about          6088       0.07%
    /courseware.views:course_info           847180     10.23%
    /courseware.views:course_survey         43         0.00%
    /courseware.views:index                 4163742    50.26%
    /courseware.views:jump_to               4989       0.06%
    /courseware.views:jump_to_id            87845      1.06%
    /courseware.views:mktg_course_about     2694565    32.52%
    /courseware.views:progress              331582     4.00%
    /courseware.views:static_tab            148526     1.79%
    /courseware.views:submission_history    172        0.00%
    /courseware.views:syllabus              3          0.00%
    """

    @task(50)
    def index(self):
        """
        Request a randomly-chosen top-level page in the course.
        """
        path = 'courseware' + self.course_data.courseware_path
        self.get(path, name='courseware:index')

    @task(10)
    def course_home(self):
        """
        Requests the main course home page that contains the course outline.
        """
        self.get('course', name='courseware:course_home')

    @task(10)
    def info(self):
        """
        Request the course info tab.
        """
        self.get('info', name='courseware:course_info')

    @task(4)
    def progress(self):
        """
        Request the progress tab.
        """
        self.get('progress', name='courseware:progress')

    @task(1)
    def about(self):
        """
        Request the LMS' internal about page for this course.
        """
        self.get('about', name='courseware:about')

    @task(8)
    def stop(self):
        """
        Switch to another TaskSet.
        """
        self.interrupt()
