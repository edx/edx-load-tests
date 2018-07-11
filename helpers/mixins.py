class HeadersTaskSetMixin(object):
    @property
    def post_headers(self):
        """
        Boilerplate headers for HTTP POST.
        """
        return {
            'X-CSRFToken': self.client.cookies.get('csrftoken', ''),
            'Referer': self.locust.host
        }


class EnrollmentTaskSetMixin(HeadersTaskSetMixin):
    """ TaskSet mixin with enrollment-related functionality. """

    def enroll(self, course_id):
        """
        Enrolls the test's user in the course under test.
        """
        success = True
        with self.client.post(
            '/change_enrollment',
            data={'course_id': course_id, 'enrollment_action': 'enroll'},
            headers=self.post_headers,
            name='enroll',
            catch_response=True
        ) as response:
            if response.status_code == 400:
                response.failure(
                    "Enrollment failed. Check to make sure that the course key is correct, "
                    "that the course is open for enrollment, and that that the course enrollment isn't full."
                )
                success = False
        return success
