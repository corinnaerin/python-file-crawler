import errno
import logging
from datetime import datetime
from os import walk
from os.path import join
from pprint import pformat
from re import MULTILINE

from binaryornot.check import is_binary

from file_crawler_args import FileCrawlerArgs


class FileCrawler:
    def __init__(self):

        # Create our logging instance
        self.logger = logging.getLogger('file_crawler')
        self.logger.setLevel(logging.INFO)
        log_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        log_handler.setFormatter(formatter)
        self.logger.addHandler(log_handler)

        self.args = FileCrawlerArgs().args

        self.results = {}
        self.error_files = []
        self.ignored = []

        if self.args.verbose:
            self.logger.setLevel(logging.DEBUG)

    # Returns an object hash from directory name to the number of files that match the keyword
    def get_results(self):
        self._start()

        # Recursively walk through all of the files & directories in the root
        for current_dir, dirs, files in walk(self.args.root_dir, followlinks=self.args.follow_symlinks):
            self.results[current_dir] = self._count_matching_files(current_dir, files)

            # Filter out directories that should be excluded from processing
            # It's a bit confusing, because dirs is not just a block-scoped value containing the directories
            # in the current directory. It's also used by walk() to continue recursing. So you can remove
            # directories from the list to prevent it from stepping into them. But it does make for a call pattern
            # that's somewhat difficult to follow
            self._filter_hidden_dirs(current_dir, dirs)

        self._done()
        return self.results

    # Logs the start time
    def _start(self):
        self.start_time = datetime.now()
        self.logger.info("Starting to scan {0} for files matching {1}"
                         .format(self.args.root_dir, self.args.keyword.pattern))

    # Handles logging final messages
    def _done(self):

        num_errors = self.error_files.__len__()
        if num_errors > 0:
            self.logger.warn("{0} files could not be read. Run with --version to see the full details."
                             .format(num_errors))
            self.logger.debug("All errored files:\n" + pformat(self.error_files))

        num_ignored = self.ignored.__len__()
        if num_ignored > 0:
            self.logger.warn("{0} files/directories were ignored. Run with --verbose to see the full details"
                             .format(num_ignored))
            self.logger.debug("All ignored files:\n" + pformat(self.ignored))

        self.logger.info("Done! Final result:\n" + pformat(self.results))

        end_time = datetime.now()
        run_time = end_time - self.start_time
        self.logger.info("Finished in {0} ms".format(run_time.total_seconds() * 1000))

    # checks whether the file / directory should be excluded from computation
    def _should_exclude(self, name, full_path, is_file):
        exclude = False

        if not self.args.include_hidden and name.startswith('.'):
            self.logger.debug("Ignoring hidden file/directory {0}".format(full_path))
            exclude = True

        elif is_file and is_binary(full_path):
            self.logger.debug("Ignoring binary file {0}".format(full_path))
            exclude = True

        if exclude:
            self.ignored.append(full_path)

        return exclude

    # generator function that yields only non-binary and (if specified by CLI option
    # non-hidden files
    def _files_generator(self, current_dir, names):
        for name in names:
            full_path = join(current_dir, name)
            if not self._should_exclude(name, full_path, True):
                yield full_path

    # (If specified by CLI option) filter out hidden directories from the list
    def _filter_hidden_dirs(self, current_dir, names):
        # Unfortunately walk() requires that the dirs list MUST be modified in place
        # If we use list comprehension to create a new list and overwrite the existing
        # variable, it won't actually skip these values
        for i in reversed(range(len(names))):
            full_path = join(current_dir, names[i])
            if self._should_exclude(names[i], full_path, False):
                del names[i]

    # Check each of the files in the current_dir to see if their contents match the keyword
    def _count_matching_files(self, current_dir, files):
        matching_files_count = 0

        for file_path in self._files_generator(current_dir, files):
            self.logger.debug("Processing {0}".format(file_path))
            if self._check_file(file_path):
                self.logger.debug("Found match in {0}".format(file_path))
                matching_files_count = matching_files_count + 1

        return matching_files_count

    # Check the file to see if it matches the passed regular expression
    def _check_file(self, file_path):
        try:
            fp = open(file_path)
        except IOError as e:
            # If there's a problem opening the file, we don't want to fail the entire request.
            if e.errno == errno.EACCES:
                self.logger.exception("Skipping {0} due to a permissions error".format(file_path))
                return
            self.logger.exception("Unable to open {0}".format(file_path))
        else:
            with fp:
                file_contents = fp.read()
                # Don't even have to bother manually iterating over each line individually, since
                # we can just do a multiline regex search. Using search() instead of match() here
                # because we want the regular expression to match any line in the file. So if the pattern starts with ^,
                # we want the file to match if ANY line matches, not just the first line.
                return self.args.keyword.search(file_contents, MULTILINE)


file_crawler = FileCrawler()
results = file_crawler.get_results()
