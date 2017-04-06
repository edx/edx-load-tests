#!/usr/bin/env bash
set -e
set -x

###############################################################################
#
# run-loadtest.sh
#
# Start a parameterized loadtest. This script is designed to be the entry
# point for various automation systems (jenkins is currently supported).
#
# Assumptions:
# * The assumptions made by util/${AUTOMATION_TOOL}-common.sh are also
#   fulfilled, if you are using ${AUTOMATION_TOOL}.
# * This script is invoked from the root of the edx-load-tests repo.
# * The required environment variables are defined.
# * pip is available.
#
# Required environment variables:
# * TARGET_URL: The target to load test.
# * TEST_COMPONENT: Which component of the target to load test.
# * NUM_CLIENTS: The number of locust clients to hatch.
# * HATCH_RATE: Hatches per second during locust ramp-up.
#
# Optional environment variables:
# * MAX_RUN_TIME - Automatically stop the loadtest after this amount of time.
#   The formatting of this value follows the timeout(1) duration spec.
# * OVERRIDES_FILES - space-delimited list of filenames of settings files.
#   These settings files will override the default settings in the order given.
#
###############################################################################

error() {
    error_message="$1"
    echo "${error_message}"
    exit 1
}

if [ -n "${JENKINS_HOME}" ] ; then
    source util/jenkins-common.sh
else
    error "ERROR: Could not detect automation system."
fi

test -z "${TARGET_URL}" && error 'TARGET_URL parameter was not specified.'
test -z "${TEST_COMPONENT}" && error 'TEST_COMPONENT parameter was not specified.'
test -z "${NUM_CLIENTS}" && error 'NUM_CLIENTS parameter was not specified.'
test -z "${HATCH_RATE}" && error 'HATCH_RATE parameter was not specified.'

# Make sure we have access to scripts, such as merge_settings.
pip install -e .

final_settings_file=settings_files/${TEST_COMPONENT}.yml

mkdir results

# In case the automation system archives workspaces, we should make an attempt
# to prevent settings files containing secrets from lingering.
cleanup() {
    echo "cleaning up lingering settings file..."
    rm $final_settings_file
}
trap cleanup TERM  # SIGTERM implies jenkins abort button was pressed

default_settings="settings_files/${TEST_COMPONENT}.yml.example"
merge_settings $default_settings $OVERRIDES_FILES > $final_settings_file

# Setup requirements for running a loadtest against the given component.
make ${TEST_COMPONENT}

# Setup locust command
locust_cmd="locust \
    --host=${TARGET_URL} -f loadtests/${TEST_COMPONENT} \
    --no-web --clients=${NUM_CLIENTS} --hatch-rate=${HATCH_RATE}"

# Install a timeout if the MAX_RUN_TIME parameter was specified.  The
# --kill-after=10s option indicates that if locust has not exited after
# receiving SIGTERM, kill it forcefully (SIGKILL).
if [ -n "${MAX_RUN_TIME}" ]; then
    locust_cmd="timeout --signal=TERM --kill-after=10s $MAX_RUN_TIME $locust_cmd"
fi

# Setup simultaneous logging to console + logfile, and run test
($locust_cmd) 2>&1 | tee results/log.txt

cleanup
