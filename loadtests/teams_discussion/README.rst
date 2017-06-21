Teams Discussion Load Testing
=============================

This directory contains Locust tasks designed to exercise teams discussion
behavior on the LMS and the teams API.

Course Setup
------------

You must select a course to run this test against, and enable the teams feature
following these instructions:

http://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/latest/course_features/teams/teams_setup.html#enable-and-configure-teams

You must also create at least one team for the locust clients to join.  The
product of ``max_team_size``, and the number of teams you create is the maximum
number of locust clients you can spawn.  Before re-running this test, remember
to manually delete the team enrollments, or just recreate new teams.

Settings
--------

Load tests are configured using a YAML file in the standard fashion.

Use the course that you set up (see section "Course Setup" above) for the
``COURSE_ID`` setting.
