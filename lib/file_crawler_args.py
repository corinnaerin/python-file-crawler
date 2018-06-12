import argparse
import os
import re
import sre_constants


def get_cli_args(manager):
    parser = __create_parser()
    return parser.parse_args(namespace=manager.Namespace())


# Custom arg type to convert into an absolute path
def __directory(dirname):
    if os.path.isdir(dirname):
        return os.path.abspath(dirname)
    else:
        error_message = "{0} is not a valid directory".format(dirname)
        raise argparse.ArgumentTypeError(error_message)


# Custom arg type to compile into a regular expression object
def __regexp(keyword):
    try:
        return re.compile(keyword)
    except sre_constants.error as error:
        error_message = "'{0}' is not a valid regular expression: {1}".format(keyword, error)
        raise argparse.ArgumentTypeError(error_message)


def __create_parser():
    # Create an argument parser so we don't have to mess with sys.argv ourselves
    parser = argparse.ArgumentParser(description='Search directory for matching files. '
                                                 'NOTE: file patterns are not regular expressions or globs. '
                                                 'They are Unix shell-style wildcards that will be matched against the '
                                                 'absolute path of the file (even if you specified '
                                                 'a relative root_dir path). '
                                                 'See https://docs.python.org/2.7/library/fnmatch.html for details.')
    parser.add_argument('root_dir', type=__directory, help='root directory to search')
    parser.add_argument('keyword', type=__regexp, help='keyword (regular expression) to search for')
    parser.add_argument('-d', '--include-hidden', action='store_const', default=False, const=True,
                        help='whether to include hidden files & directories. defaults to False.')
    parser.add_argument('-f', '--follow-symlinks', action='store_const', default=False, const=True,
                        help='whether to follow symlinks. defaults to False.')
    parser.add_argument('-v', '--verbose', action='store_const', default=False, const=True,
                        help='whether to decrease the log level from INFO to info. defaults to False.')
    parser.add_argument('-i', '--include',
                        help='pattern for files & directories that should be included. If specified, nothing '
                             'that doesn\'t match this pattern will be included.')
    parser.add_argument('-e', '--exclude',
                        help='pattern for files & directories that should be excluded. Can be used in '
                             'conjunction with --include to narrow down further.')

    return parser
