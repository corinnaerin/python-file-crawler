import logging
from os import path
from pprint import pformat
from threading import Lock


class FileCrawlerResults:
    def __init__(self):
        self.__results = dict()
        self.__errors = []
        self.__ignored = []
        self.file_count = 0
        self.__results_lock = Lock()

    def lock(self):
        self.__results_lock.acquire()

    def release(self):
        self.__results_lock.release()

    def add_directory(self, dir_name):
        self.lock()
        self.__results[dir_name] = 0
        self.release()

    def has_directory(self, dir_name):
        self.lock()
        has_dir = dir_name in self.__results
        self.release()
        return has_dir

    def log_file(self, file_path, match):
        self.lock()
        self.file_count = self.file_count + 1
        if match:
            dir_name = path.dirname(file_path)
            count = self.__results[dir_name] + 1
            self.__results[dir_name] = count
        self.release()

    def log_error(self, file_path):
        self.lock()
        self.__errors.append(file_path)
        self.release()

    def log_ignored(self, file_path):
        self.lock()
        self.__ignored.append(file_path)
        self.release()

    def dump(self):
        self.lock()
        num_errors = len(self.__errors)
        if num_errors > 0:
            logging.warn("{0} files could not be read. Run with --version to see the full details."
                         .format(num_errors))
            logging.info("All errored files:\n" + pformat(self.__errors))

        num_ignored = len(self.__ignored)
        if num_ignored > 0:
            logging.warn("{0} files/directories were ignored. Run with --verbose to see the full details"
                         .format(num_ignored))
            logging.info("All ignored files/directories:\n" + pformat(self.__ignored))

        logging.info("Results:\n" + pformat(self.__results))
        self.release()
