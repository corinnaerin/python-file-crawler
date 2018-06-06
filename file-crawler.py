import argparse
import os
import re
import sre_constants


# Custom arg type to convert into an absolute path
def directory(dirname):
    if os.path.isdir(dirname):
        return os.path.abspath(dirname)
    else:
        error_message = "{0} is not a valid directory".format(dirname)
        raise argparse.ArgumentTypeError(error_message)


# Custom arg type to compile into a regular expression object
def regexp(keyword):
    try:
        return re.compile(keyword)
    except sre_constants.error as error:
        error_message = "{0} is not a valid regular expression: {1}".format(keyword, error)
        raise argparse.ArgumentTypeError(error_message)


def get_args():
    # Create an argument parser so we don't have to mess with sys.argv ourselves
    parser = argparse.ArgumentParser(description='Search directory for matching files')
    parser.add_argument('root_dir', type=directory, help='root directory to search')
    parser.add_argument('keyword', type=regexp, help='keyword (regular expression) to search for')
    parser.add_argument('-i', '--include-hidden', action='store_const', default=False, const=True,
                        help='whether to include hidden files & directories. defaults to False.')
    parser.add_argument('-f', '--follow-symlinks',  action='store_const', default=False, const=True,
                        help='whether to follow symlinks. defaults to False.')

    return parser.parse_args()

args = get_args()
print args
