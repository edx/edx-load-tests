#!/usr/bin/env python
#
# Get the latest transaction distribution for the module_render subtask of the
# LMS load test.
#
# Instructions:
#
# 1. Go to the the prod-edx-edxapp-lms transactions table in newrelic:
#
#     https://rpm.newrelic.com/accounts/88178/applications/3343327/transactions/table
#
# 2. Change time period to last 7 days
#
# 3. Export a CSV of the data
#
# 4. Pipe that file (controller_summary.csv below) into this script:
#
#      ./lms_module_render_tx_distribution.py < controller_summary.csv
#
# 5. Copy the output and paste it into correct place in
#    loadtests/lms/module_render.py for future reference.
#
# Lets keep this script python 2/3 compatible since it's standalone and so
# simple.

import sys

import fileinput
import csv


def main():

    # fileinput takes input data from stdin or the filename in the first argument
    data = csv.reader(fileinput.input())

    # Set aside the first row, since it isn't data.  We'll use it to infer field
    # indexes.
    fields = next(data)

    if 'Count' not in fields:
        raise Exception('Count field not found')
    if 'Action' not in fields:
        raise Exception('Action field not found')

    # we're only concerned about the Count and Action fields
    count_idx = fields.index('Count')
    action_idx = fields.index('Action')

    # filter out irrelevant data
    data = filter(
        lambda record: record[action_idx].startswith('/XBlock/Handler'),
        data
    )

    # sort by count
    data_sorted = sorted(data, key=lambda record: float(record[count_idx]), reverse=True)

    # the total count is used to help normalize counts to percentages
    total_count = sum((float(record[count_idx]) for record in data_sorted))

    # extract relevant fields and format/normalize them appropriately
    count_data_formatted = (
        [record[action_idx], '{:.2f}%'.format(100 * float(record[count_idx]) / total_count)]
        for record in data_sorted
    )

    # display results on stdout in CSV format
    csv.writer(sys.stdout).writerows(count_data_formatted)


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
