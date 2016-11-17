#!/bin/bash
#
# Get the latest transaction distribution for the LMS load test.  This script
# tested using GNU coreutils and many versions of awk.
#
# Instructions:
#
# 1. Download a CSV from the prod-edx-edxapp-lms transactions table in newrelic:
#
#     https://rpm.newrelic.com/accounts/88178/applications/3343327/transactions/table
#
# 2. Pipe that file (controller_summary.csv below) into this script:
#
#     ./lms_tx_distribution.sh < controller_summary.csv
#
# 3. Copy the output and paste it into correct place in
# loadtests/lms/locustfile.py for future reference.


# specifies which field number is the transaction count
COUNT_FIELD=3

# discard the first line: the field names
read fields

# uncomment for debugging field order and to fix COUNT_FIELD if necessary
# echo $fields

# extract irrelevant columns/fields (the locust task ratios only derived from
# transaction counts)
data_only_count=$(cut -d, -f1,$COUNT_FIELD)

# rename transactions starting with /XBlock/Handlers since they just appear to
# be a passthrough to /courseware.module_render:handle_xblock_callback
data_fix_xb_handlers=$(echo "$data_only_count" | sed 's|^/XBlock/Handler|/courseware.module_render:XBlock/Handler|')

# group transactions by module
data_grouped_by_module=$(echo "$data_fix_xb_handlers" | awk -F, '
    BEGIN { OFS="," }
    NR==1 { print }
    NR>1 { split($1, parts, ":"); name = parts[1]; a[name] += $2 }
    END { for (n in a) print n" Total",a[n] }
')

# convert raw transaction counts to percentages of the overall total
data_percentages=$(echo "$data_grouped_by_module" | awk -F, '
    BEGIN { OFS="," }
    NR==1 { total = $2 }
    NR>1 { p = ($2/total)*100; printf "%s, %.2f%%\n", $1, p }
')

# sort the remaining rows
data_sorted=$(echo "$data_percentages" | sort --field-separator=, --key=2 --numeric-sort --reverse )

echo "$data_sorted"

