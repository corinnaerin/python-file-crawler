import Queue
import logging
from fnmatch import fnmatch
from os.path import join

from binaryornot.check import is_binary


class FileCrawlerDirectory:
    def __init__(self, dir_name, files):
        self.dir_name = dir_name
        self.files = files


class FileCrawlerInputs:

    def __init__(self, cli_args):
        self.dir_queue = Queue.Queue()
        self.file_queue = Queue.Queue()
        self.__cli_args = cli_args

    # checks whether the file / directory should be excluded from computation
    def _should_exclude(self, name, full_path, is_file, results):
        exclude = False

        if not is_file and results and results.has_directory(full_path):
            logging.warn("Already processed %s, most likely due to an infinite loop of symbolic links" % full_path)
            exclude = True

        if not self.__cli_args.include_hidden and name.startswith('.'):
            logging.debug("Ignoring hidden file/directory {0}".format(full_path))
            exclude = True

        elif is_file:
            if is_binary(full_path):
                logging.debug("Ignoring binary file {0}".format(full_path))
                exclude = True

            elif self.__cli_args.include and not fnmatch(full_path, self.__cli_args.include):
                logging.debug("Ignoring file {0} that does not match include glob".format(full_path))
                exclude = True

            elif self.__cli_args.exclude and fnmatch(full_path, self.__cli_args.exclude):
                logging.debug("Ignoring file {0} that matches exclude glob".format(full_path))
                exclude = True

        if exclude:
            results.log_ignored(full_path)

        return exclude

    # add files to the queue, but only non-binary and (if specified by CLI option)
    # non-hidden files
    def add_files_to_queue(self, current_dir, files, results):
        for name in files:
            full_path = join(current_dir, name)
            if not self._should_exclude(name, full_path, True, results):
                self.file_queue.put(full_path)

    # (If specified by CLI option) filter out hidden directories from the list
    def filter_hidden_dirs(self, current_dir, dirs, results):
        # Unfortunately walk() requires that the dirs list MUST be modified in place
        # If we use list comprehension to create a new list and overwrite the existing
        # variable, it won't actually skip these values
        for i in reversed(range(len(dirs))):
            full_path = join(current_dir, dirs[i])
            if self._should_exclude(dirs[i], full_path, False, results):
                del dirs[i]
