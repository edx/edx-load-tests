import argparse
from collections import OrderedDict
import getpass
import sys
import textwrap
import uuid

from course_seeder import CourseSeeder
from discussions_seeder import DiscussionsSeeder


def setup_course_in_studio(args):
    """
    Setup studio and return the created course_id
    """
    print "Studio url set to: {}".format(args.studio)
    email = args.email or raw_input("Studio Email: ")
    password = args.password or getpass.getpass("Password: ")
    seeder = CourseSeeder(studio_url=args.studio)
    seeder.login_to_studio(email, password)
    unique_id = uuid.uuid4().hex[:5]
    course_data = {
        "org": "dapi",
        "course": args.action,
        "run": "test_{}".format(unique_id),
        "display_name": "dapi_name_{}".format(unique_id),
    }
    course_id = seeder.create_course(course_data=course_data)
    seeder.import_tarfile(course_id=course_id, tarfile=args.tarfile)
    return course_id


def setup_discussion_seeder(args):
    print "LMS url set to: {}".format(args.lms)
    seeder = DiscussionsSeeder(lms_url=args.lms)
    email = args.email or raw_input("LMS Email: ")
    password = args.password or getpass.getpass("Password: ")
    seeder.login_to_lms(email, password)
    return seeder


def save_course_thread_list_to_file(args, seeder=None):
    """
    Saves all threads in the course to a file.

    Arguments:
        args: Parser args.
        seeder: A DiscussionSeeder.

    """
    seeder = seeder if seeder else setup_discussion_seeder(args)
    if not args.course:
        print "Requires a course_id"
        return
    file_name = args.action
    save_threads_to_file(seeder, file_name, course_id=args.course, thread_id_list=None)


def save_threads_to_file(seeder, file_name, course_id, thread_id_list=None):
    """
    Handles printing necessary output when writing threads to a file.

    Arguments:
        seeder (DiscussionSeeder): The DiscussionSeeder.
        file_name (str): The filename to be written to.
        course_id (str): The course containing the threads.
        thread_id_list (list): A list of thread ids, or None to read all
            thread ids from the course.

    """
    print "Saving thread_ids to: {}".format(file_name)
    seeder.create_thread_data_file(file_name=file_name, course_id=course_id, thread_id_list=thread_id_list)
    print "Run locust with SEEDED_DATA={}".format(file_name)


def get_course_id(args=None, course_id=None):
    """
    Returns the course id to be used seeding.  If a course id is provided, it is
    used. Otherwise a new course is created and its course id is returned.

    Arguments:
        args: Optional parser args that could include the course, as well as
            details for setting up a new course.
        course_id: Optional course id.

    Returns:
        The course id to be used for seeding.

    """
    if course_id:
        seed_course_id = course_id
    elif args and args.course:
        seed_course_id = args.course
    else:
        seed_course_id = setup_course_in_studio(args)

    print "Run locust with COURSE_ID={}".format(seed_course_id)
    return seed_course_id


def create_threads(args, course_id=None, seeder=None, save_threads=True):
    """
    Creates threads in multiples of 10 and then returns the locust commandline

    Each thread has a ~250character body
    Of the 10 threads created
        4 have no comments/responses
        3 have some sort of flag (abused/voted/following/endorsed)
        1 has a response and a comment
        3 have a response
    Threads=10, Responses=4, comments=1
    """
    course_id = get_course_id(args, course_id)

    seeder = seeder if seeder else setup_discussion_seeder(args)
    posts = int(args.batches or raw_input("How many threads in multiples of 10?"))
    seeder.seed_threads(course_id=course_id, posts=posts)
    file_name = args.action + str(posts * 10)
    if save_threads:
        save_threads_to_file(seeder, file_name, course_id)


def create_comments(args, course_id=None, seeder=None, save_threads=True):
    """
    Creates threads, responses and comments as supplied in args or via input.

    Arguments:
        args: Parser args.
        course_id: The course id where the comments will be added.
        seeder: The DiscussionSeeder.
        save_threads: True if the new threads should be saved to a file, and False otherwise.

    """
    course_id = get_course_id(args, course_id)

    seeder = seeder if seeder else setup_discussion_seeder(args)
    posts = int(args.threads or raw_input("How many threads "))
    responses = int(args.responses or raw_input("How many responses for thread "))
    child_comments = int(args.comments or raw_input("How many comments for each response "))
    thread_list = seeder.seed_comments(course_id=course_id, posts=posts, responses=responses, child_comments=child_comments)
    file_name = args.action + str(responses * child_comments)
    if save_threads:
        save_threads_to_file(seeder, file_name, course_id, thread_id_list=thread_list)


def main():

    actions = OrderedDict([
        ("CreateThreads", {
            'function': create_comments,
            'help': 'Creates threads with the specified number of responses and comments.',
        }),
        ("CreateThreadBatches", {
            'function': create_threads,
            'help': 'Creates batches of 10 threads with random numbers of responses and comments and random anttributes.',
        }),
        ("DumpCourseThreads", {
            'function': save_course_thread_list_to_file,
            'help': 'Dumps all threads in a course to a file to use with the locust tests.',
        }),
    ])

    parser = argparse.ArgumentParser(
        description="This script can be used to seed data and output help for running locust.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('-a', '--action', help='Script action (see below).', default='', required=True)
    parser.add_argument('-s', '--studio', help='Studio url.', default='', required=True)
    parser.add_argument('-l', '--lms', help='LMS url.', default='', required=True)

    parser.add_argument('-f', '--tarfile', help='Name of the course tarfile.', default='dapi_course.tar.gz')
    parser.add_argument('-e', '--email', help='Email for login for both LMS/Studio. You will be prompted if needed and not supplied.', default='')
    parser.add_argument('-p', '--password', help='Password for both LMS/Studio. You will be prompted if needed and not supplied.', default='')
    parser.add_argument('-b', '--batches', help='Number of custom 10 thread batches. You will be prompted if needed and not supplied.', default='')
    parser.add_argument('-t', '--threads', help='Number of threads. You will be prompted if needed and not supplied.', default='')
    parser.add_argument('-r', '--responses', help='Number of responses per thread. You will be prompted if needed and not supplied.', default='')
    parser.add_argument('-m', '--comments', help='Number of comments per response. You will be prompted if needed and not supplied.', default='')
    parser.add_argument('-c', '--course', help='Course id for adding threads.  If not supplied, a course will be created for you.', default='')

    parser.epilog = "script actions/tasks:"
    for action in actions:
        parser.epilog += "\n    {}".format(action)
        LINE_LENGTH = 80
        TWO_INDENTS = 8
        for line in textwrap.wrap(actions[action]['help'], LINE_LENGTH - TWO_INDENTS):
            parser.epilog += "\n        {}".format(line)

    args = parser.parse_args()

    if args.action not in actions:
        parser.print_help()
        return -1

    actions[args.action]['function'](args)

if __name__ == "__main__":
    sys.exit(main())
