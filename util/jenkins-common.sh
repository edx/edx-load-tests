#!/usr/bin/env bash
set -e
set -x

###############################################################################
#
# jenkins-common.sh
#
# Common setup routine for running a loadtest in a jenkins job.
#
# This script assumes the file $HOME/edx-venv_clean.tar.gz has been prepared,
# but not created within the sequence of build steps for this job.  It needs to
# have been created outside of the timeline of this jenkins job so that the
# human who started the build doesn't have to wait so long for the requirements
# to install.
#
# At edX, we bake $HOME/edx-venv_clean.tar.gz into the image which jenkins uses
# to launch a loadtest worker using the following ansile task:
#
# https://github.com/edx/configuration/blob/master/playbooks/roles/jenkins_worker/tasks/loadtest_driver_worker.yml
#
# To see an example of how a jenkins job can invoke edx load tests, refer to
# the following job DSL and wrapper script:
#
# https://github.com/edx/jenkins-job-dsl/blob/master/testeng/jobs/loadtestDriver.groovy
# https://github.com/edx/jenkins-job-dsl/blob/master/testeng/resources/run-loadtest-wrapper.sh
#
###############################################################################

# Reset the jenkins worker's virtualenv back to the
# state it was in when the instance was spun up.
if [ -e $HOME/edx-venv_clean.tar.gz ]; then
    rm -rf $HOME/edx-venv
    tar -C $HOME -xf $HOME/edx-venv_clean.tar.gz
fi

# Activate the Python virtualenv
source $HOME/edx-venv/bin/activate

echo "This node is `curl http://169.254.169.254/latest/meta-data/hostname`"
