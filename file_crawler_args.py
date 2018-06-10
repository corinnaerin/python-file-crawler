import argparse
import os
import re
import sre_constants


class FileCrawlerArgs:
    def __init__(self):
        parser = self.create_parser()
        self.args = parser.parse_args()

    # Custom arg type to convert into an absolute path
    def directory(self, dirname):
        if os.path.isdir(dirname):
            return os.path.abspath(dirname)
        else:
            error_message = "{0} is not a valid directory".format(dirname)
            raise argparse.ArgumentTypeError(error_message)

    # Custom arg type to compile into a regular expression object
    def regexp(self, keyword):
        try:
            return re.compile(keyword)
        except sre_constants.error as error:
            error_message = "'{0}' is not a valid regular expression: {1}".format(keyword, error)
            raise argparse.ArgumentTypeError(error_message)

    def create_parser(self):
        # Create an argument parser so we don't have to mess with sys.argv ourselves
        parser = argparse.ArgumentParser(description='Search directory for matching files')
        parser.add_argument('root_dir', type=self.directory, help='root directory to search')
        parser.add_argument('keyword', type=self.regexp, help='keyword (regular expression) to search for')
        parser.add_argument('-d', '--include-hidden', action='store_const', default=False, const=True,
                            help='whether to include hidden files & directories. defaults to False.')
        parser.add_argument('-f', '--follow-symlinks', action='store_const', default=False, const=True,
                            help='whether to follow symlinks. defaults to False.')
        parser.add_argument('-v', '--verbose', action='store_const', default=False, const=True,
                            help='whether to decrease the log level from INFO to info. defaults to False.')
        parser.add_argument('-i', '--include',
                            help='glob pattern for files & directories that should be included. If specified, nothing '
                                 'that doesn\'t match this glob will be included.')
        parser.add_argument('-e', '--exclude',
                            help='glob pattern for files & directories that should be excluded. Can be used in '
                                 'conjunction with --include to narrow down further.')

        return parser
