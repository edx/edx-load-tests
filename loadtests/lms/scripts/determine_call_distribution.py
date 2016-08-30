#!/usr/bin/env python
"""
A script to help determine the appropriate distribution of forums load.

TODO: This script should really have been implemented as a Splunk Dashboard.
When the Splunk dashboard is implemented, this script should be removed.

"""
import argparse
import csv
from datetime import datetime
from math import floor
import re

# skip blocked ips determined to be bots
BLOCKED_IPS = ['103.224.248.161']


class TimeResultsAggregator(object):
    """
    Tracks results based on the time of each request, including:
    - start time
    - end time
    - request count per time increment

    """
    MINUTES_PER_INCREMENT = 5
    SECONDS_PER_INCREMENT = MINUTES_PER_INCREMENT * 60

    def __init__(self):
        """
        Init method.
        """
        self.start_date = None
        self.end_date = None
        self.total_count = 0
        self.increment_counts = {}

    def track_time(self, date_string):
        """
        Tracks the request time by incrementing the count for the appropriate
        time increment of the passed date string, as well as adjusting the start
        and end times as needed.

        Arguments:
            date_string: Date string to be tracked, as exported from Splunk.

        """
        date_object = datetime.strptime(date_string.split(' ')[0], '%d/%b/%Y:%H:%M:%S')
        if self.start_date is None or date_object < self.start_date:
            self.start_date = date_object
        if self.end_date is None or self.end_date < date_object:
            self.end_date = date_object
        self.total_count += 1
        # counts calls per time increment
        increment = floor((self.end_date - self.start_date).total_seconds() / TimeResultsAggregator.SECONDS_PER_INCREMENT)
        self.increment_counts[increment] = self.increment_counts.get(increment, 0) + 1

    def print_results(self):
        """
        Prints start and end time, overall requests/second, and maximum
        requests/second for any single time increment.

        """
        print "Times and Rates:"
        print "First request: {}".format(self.start_date)
        print "Last request:  {}".format(self.end_date)
        print "Overall average requests/second: {}".format(
            round(self.total_count / (self.end_date - self.start_date).total_seconds(), 3)
        )
        max_increment_count = max(self.increment_counts.itervalues())
        print "Maximum average requests/second over {increment_minutes} minutes: {rate}".format(
            increment_minutes=TimeResultsAggregator.MINUTES_PER_INCREMENT,
            rate=round(float(max_increment_count) / TimeResultsAggregator.SECONDS_PER_INCREMENT, 3)
        )


class EndpointCounterList(object):
    """
    Tracks counts for a list of endpoint counters.

    Only a single endpoint counter is allowed to count each request.  The first
    that matches will count the request, and thus order matters.

    """
    def __init__(self, counter_list):
        """
        Init method.

        Arguments:
            counter_list (list of EndpointCounters): An ordered list of endpoint
                counters to be used to count requests per endpoint.  The first
                endpoint counter to match a request will count it.

        """
        self.total_count = 0
        self.other_count = 0
        self.counter_list = counter_list

    def track_request(self, uri):
        """
        Tracks a request by having the first matching endpoint counter count the
        request.  Any request that doesn't match any endpoint counter is tracked
        under "other".

        Arguments:
            uri (string): The URI of the request.

        """
        found_match = False
        for counter in self.counter_list:
            found_match = counter.match_and_increment(uri)
            if found_match:
                break
        if found_match is False:
            self.other_count += 1
        self.total_count += 1

    def print_counts(self):
        """
        Prints the count results for each endpoint counter, as well as the
        "other" requests and the total requests.

        """
        print "Endpoint Details:"
        sorted_counter_list = sorted(self.counter_list, key=lambda x: x.count, reverse=True)
        for counter in sorted_counter_list:
            counter.print_count(self.total_count)

        if self.other_count > 0:
            print_count("Other count", self.other_count, self.total_count)

        print "TOTAL count: {}".format(self.total_count)


class EndpointCounter(object):
    """
    Tracks request counts for an endpoint.

    """
    def __init__(self, description, regex, key_counter_list=None):
        """
        Init method.

        Arguments:
            description (string): Description of the endpoint.
            regex (string): A regex used to determine if a request matches this
                endpoint.
            key_counter_list (list of GroupCounters): An optional list of
                GroupCounters that could be used to further break down counts
                within a particular endpoint.

        """
        self.count = 0
        self.description = description
        self.regex = regex
        self.key_counter_list = key_counter_list if key_counter_list else []

    def match_and_increment(self, uri):
        """
        Increments the request count if and only if the provided URI matches
        this endpoint.

        Arguments:
            uri (string): The URI of the request to be tracked.

        Returns:
            True if the URI matches this endpoint, False otherwise.

        """
        match = re.search(self.regex, uri)
        if match:
            self.count += 1
            for key_counter in self.key_counter_list:
                key_counter.increment(uri)
        return match is not None

    def print_count(self, total_count):
        """
        Prints the request count results for this endpoint.

        Arguments:
            total_count (int): The total count of requests to be used to print
                percentages.

        """
        INDENT = "    "
        print_count(self.description, self.count, total_count)
        for key_counter in self.key_counter_list:
            key_counter.print_top_keys(INDENT)


class KeyCounter(object):
    """
    Tracks counts for a set of related keys.

    """
    def __init__(self, description):
        """
        Init method.

        Arguments:
            description (string): A description of the related keys.

        """
        self.total_count = 0
        self.key_counts = {}
        self.description = description

    def increment(self, key):
        """
        Increments the count for the provided key.

        Arguments:
            key (string): The key for which the count will be incremented.

        """
        self.key_counts[key] = self.key_counts.get(key, 0) + 1
        self.total_count += 1

    def print_top_keys(self, indent=''):
        """
        Since there may be many keys that are counted, only the top key counts
        will be printed.

        Arguments:
            indent (string): A prefix of spaces used to indent the output
            appropriately.

        """
        NUMBER_OF_TOP_KEYS = 5
        sorted_keys = sorted(self.key_counts.items(), key=lambda x: x[1], reverse=True)
        top_count = min(NUMBER_OF_TOP_KEYS, len(sorted_keys))
        print "{indent}{description} (top {top_count} of {total}):".format(
            indent=indent,
            description=self.description,
            top_count=top_count,
            total=len(self.key_counts),
        )
        for index in range(0, top_count):
            print_count(sorted_keys[index][0], sorted_keys[index][1], self.total_count, indent + "- ")


class RegexGroupCounter(KeyCounter):
    """
    A specialized key counter that tracks the counts for strings matched against
    a regex with a named group, where the named group values are used as the
    keys.

    """
    # key used when the regex doesn't match a provided string
    NO_MATCH = "no match"

    def __init__(self, description, regex):
        """
        Init method.

        Arguments:
            description (string): A description of the related keys.
            regex (string): A regex with a named group to be used to count
                matching strings.
        """
        super(RegexGroupCounter, self).__init__(description)
        self.regex = regex
        match = re.search('\?P\<(?P<group_id>\w+)\>', self.regex)
        if match:
            self.group_id = match.group('group_id')
        else:
            raise ValueError("RegexGroupCounter must be initialized with a regex including '?P<some_group_id>'.")

    def increment(self, string):
        """
        Increments the key count for the key pulled from the string using the
        previously supplied regex and named group.

        Arguments:
            string (string): The string to be sorted and counted according to
                the key pulled from the string using the previously supplied
                regex and named group.

        """
        group_id = RegexGroupCounter.NO_MATCH
        match = re.search(self.regex, string)
        if match:
            group_id = match.group(self.group_id)
        super(RegexGroupCounter, self).increment(group_id)


def parse_splunk(csv_path):
    """
    Loads Splunk export CSV, parses, and outputs results.

    Sample splunk search for Discussions requests:

        index="prod-edx" sourcetype=nginx URI="*/discussion/*" AND NOT URI="*/static/css/discussion/*"

    CSV export row headers from Splunk:

        HTTP,SURL,URI,URL,"_raw","_time","activate_block_id",ajax,am,"api_key","auth_entry",authuser,browser,btmpl,
        bytes,"cancel_url",cd,child,code,"commentable_ids",continue,date,"date_hour","date_mday","date_minute",
        "date_month","date_second","date_wday","date_year","date_zone","discussion_page",display,"django_app",
        duration,ei,env,esrc,eventtype,fid,flagged,"group_id",hl,host,hr,index,"ip_address",k,linecount,locale,
        "log_level","logger_id","mark_as_read",method,mi,mso,next,oauth,page,passive,pid,prompt,punct,
        "python_line_num","python_module",rand,rct,recursive,"redirect_state",referer,"remote_ip","request_id",
        "resp_limit","resp_skip","response_time",sa,sarp,scc,"service_variant","session_state","signed_next",
        "skip_api_login","sort_key","sort_order",source,sourcetype,"splunk_server","splunk_server_group",state,
        "status_code","target_ip",text,th,tid,timeendpos,timestamp,timestartpos,unanswered,unread,url,"user_id",
        username,usg,v,ved

    Arguments:
        csv_path (str): The path of the csv file.

    """
    time_results_aggregator = TimeResultsAggregator()
    endpoint_counter_list = discussion_counter_list()
    course_counter = RegexGroupCounter("Courses", 'courses/(?P<course_key>.+)/discussion')
    remote_ip_counter = KeyCounter("Remote IPs")

    # Loop over splunk csv and count requests
    with open(csv_path, 'rb') as csvfile:
        csvdata = csv.DictReader(csvfile, delimiter=',', quotechar='"')

        for row in csvdata:
            # skip blocked ips determined to be bots
            if row['remote_ip'] in BLOCKED_IPS:
                continue
            elif is_countable_discussions_uri(row['URI']) is False:
                continue

            time_results_aggregator.track_time(row['date'])
            endpoint_counter_list.track_request(row['URI'])
            course_counter.increment(row['URI'])
            # counts for remote ips (helpful to identify potential bots)
            remote_ip_counter.increment(row['remote_ip'])

    # Print results
    time_results_aggregator.print_results()
    print ""
    endpoint_counter_list.print_counts()
    print ""
    course_counter.print_top_keys()
    print ""
    remote_ip_counter.print_top_keys()


def print_count(description, count, total_count, indent=''):
    """
    Prints the results for a single count, including its percent.

    Arguments:
        description (string): A description of the count.
        count (int): The count to be printed.
        total_count (int): Total count used to calculate percentage.
        indent (string): A prefix string that can be used for the output.

    """
    print "{indent}{description}: {count} ({percent}%)".format(
        indent=indent,
        description=description,
        count=count,
        percent=(100 * count / total_count),
    )


def is_countable_discussions_uri(uri):
    """
    Determines if the URI should be counted at all.  Some URIs, like static css,
    need to be skipped.

    Arguments:
        uri (string): The URI of the request.

    Returns:
        True if the request should be counted, False otherwise.

    """
    return re.search('/static/css/discussion', uri) is None


def discussion_counter_list():
    """
    Creates an EndpointCounterList that is appropriate for Discussions
    endpoints.

    Returns:
        An EndpointCounterList to be used to count requests for Discussions
        endpoints.

    """
    # Sample other calls include:
    #   flagAbuse, unFlagAbuse, upvote, unvote, follow, delete
    return EndpointCounterList([
        EndpointCounter("Mobile API count", '/api/discussion/v1/'),
        EndpointCounter("Read thread count", 'discussion/forum/.+/threads/\w+', key_counter_list=[
            RegexGroupCounter("Threads IDs", 'discussion/forum/.+/threads/(?P<thread_id>\w+)')
        ]),
        EndpointCounter("Create thread count", 'discussion/.+/threads/create\?'),
        EndpointCounter("Update thread count", 'discussion/threads/.+/update\?'),
        EndpointCounter("Create response count", 'discussion/threads/.+/reply\?'),
        EndpointCounter("Create comment count", 'discussion/comments/.+/reply\?'),
        EndpointCounter("Update comment count", 'discussion/comments/.+/update\?'),
        EndpointCounter("Read inline count", 'discussion/forum/.+/inline\?'),
        EndpointCounter("User profile count", 'discussion/forum/users/'),
        # Where in the UI does discussion/users get called?
        EndpointCounter("User count", 'discussion/users\?'),
        EndpointCounter("Forum tab count", 'discussion/forum$'),
        EndpointCounter("Forum search count", 'discussion/forum/search\?'),
        EndpointCounter("Topic filter count", 'discussion/forum\?'),
    ])


def main():
    """
    Used to execute the script. Use --help option for help.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Determines the call distribution from data dumped from splunk.",
    )
    parser.add_argument('filename', help="The csv file name exported from Splunk.")

    args = parser.parse_args()

    parse_splunk(args.filename)


if __name__ == '__main__':
    main()
