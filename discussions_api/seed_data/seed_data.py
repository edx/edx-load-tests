import argparse
import getpass
import sys
import uuid

from course_seeder import CourseSeeder
from discussions_seeder import DiscussionsSeeder


def setup_studio(args):
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


def setup_lms(args):
    print "LMS url set to: {}".format(args.lms)
    seeder = DiscussionsSeeder(lms_url=args.lms)
    email = args.email or raw_input("LMS Email: ")
    password = args.password or getpass.getpass("Password: ")
    seeder.login_to_lms(email, password)
    return seeder


def save_thread_list_to_file(args, seeder=None):
    seeder = seeder if seeder else setup_lms(args)
    if not args.course:
        print "Requires a course_id"
        return
    file_name = args.action
    print "Saving thread_ids to: {}".format(file_name)
    seeder.create_thread_data_file(file_name=file_name, course_id=args.course)
    return


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
    course_id = course_id if course_id else setup_studio(args)
    seeder = seeder if seeder else setup_lms(args)
    posts = int(args.number or raw_input("How many threads in multiples of 10?"))
    seeder.seed_threads(course_id=course_id, posts=posts)
    file_name = args.action + str(posts * 10)
    if save_threads:
        print "Saving thread_ids to: {}".format(file_name)
        seeder.create_thread_data_file(file_name=file_name, course_id=course_id)
    return "LOCUST_TASK_SET={} COURSE_ID={} SEEDED_DATA={} locust --host={} ".format(
        args.action,
        course_id,
        file_name,
        args.lms,
    )


def create_comments(args, course_id=None, seeder=None, save_threads=True):
    """
    Creates comments in multiples of 20 and then returns the locust commandline
    """
    course_id = course_id if course_id else setup_studio(args)
    seeder = seeder if seeder else setup_lms(args)
    posts = int(args.number or raw_input("How many responses that have comments in multiples of 20"))
    seeder.seed_comments(course_id=course_id, posts=posts)
    file_name = args.action + str(posts * 20)
    if save_threads:
        print "Saving thread_ids to: {}".format(file_name)
        seeder.create_thread_data_file(file_name=file_name, course_id=course_id)
    return "LOCUST_TASK_SET={} COURSE_ID={} SEEDED_DATA={} locust --host={} ".format(
        args.action,
        course_id,
        file_name,
        args.lms,
    )


def return_course(args, course_id=None):
    """
    Returns the commandline for locust with the given course_id
    """
    course_id = course_id if course_id else setup_studio(args)
    return "LOCUST_TASK_SET={} COURSE_ID={} locust --host={} ".format(
        args.action,
        course_id,
        args.lms,
    )


def setup_flow_test(args):
    """
    Predefined test for running a loadtest against all endpoints.

    Median Posts in a course is ~2000
    Average comments on a thread ~1.5
    """
    course_id = setup_studio(args)
    seeder = setup_lms(args)
    args.number = 100
    create_threads(args, course_id, seeder, False)
    args.number = 6
    create_comments(args, course_id, seeder, True)
    print "LOCUST_TASK_SET={} COURSE_ID={} SEEDED_DATA={} locust --host={} ".format(
        "DiscussionsApiTest",
        course_id,
        args.action,
        args.lms,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.usage = '''
    This script will output the command to be used for the locustfile.

    Test types:
        GetThreadsTask:
        GetCommentsTasks:
        PatchThreadsTask:
        PostThreadsTask:
        SaveThreads:
        FlowTest:

    Required:
    -a  --action    Script actions
    -s  --studio    Studio url
    -l  --lms       LMS url

    Optional:
    -f  --tarfile   Name of the course tarfile
    -e  --email     Email for login for both LMS/Studio
    -p  --password  Password for both LMS/Studio
    -n  --number    Number of Threads/Comments
    -c  --course    Course_id when saving threads
    '''
    parser.add_argument('-a', '--action', help='Script action', default="")
    parser.add_argument('-s', '--studio', help='Studio', default="")
    parser.add_argument('-l', '--lms', help='LMS', default="")
    parser.add_argument('-f', '--tarfile', help='Tarfile', default='dapi_course.tar.gz')
    parser.add_argument('-e', '--email', help='email', default='')
    parser.add_argument('-p', '--password', help='password', default='')
    parser.add_argument('-n', '--number', help='number of Threads/Comments', default='')
    parser.add_argument('-c', '--course', help='Course that holds threads', default='')

    args = parser.parse_args()

    list_of_actions = [
        "GetCommentsTasks",
        "GetThreadsTask",
        "PatchThreadsTask",
        "PostThreadsTask",
        "SaveThreads",
        "FlowTest"
    ]

    if args.action not in list_of_actions:
        parser.print_usage()
        return -1

    setup_test = {
        "GetThreadsTask": create_threads,
        "PatchThreadsTask": create_threads,
        "GetCommentsTasks": create_comments,
        "SaveThreads": save_thread_list_to_file,
        "PostThreadsTask": return_course,
        "FlowTest": setup_flow_test,
    }

    setup_test[args.action](args)

if __name__ == "__main__":
    sys.exit(main())
