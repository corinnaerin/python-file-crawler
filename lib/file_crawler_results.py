import logging
from os import path
from pprint import pformat


class FileCrawlerResults:
    def __init__(self, log_level):
        self.__logger = logging.getLogger('file_crawler.FileCrawlerResults')
        # For some reason, the level isn't being inherited from the parent logger,
        # even though the formatter & handler are.... weird
        self.__logger.setLevel(log_level)
        self.__results = dict()
        self.file_count = 0
        self.__errors = list()
        self.__ignored = list()

    def add_directory(self, dir_name):
        self.__results[dir_name] = 0

    def has_directory(self, dir_name):
        return dir_name in self.__results

    def log_match(self, file_path):
        dir_name = path.dirname(file_path)
        count = self.__results[dir_name] + 1
        self.__results[dir_name] = count

    def increment_counter(self):
        self.file_count += 1

    def get_file_count(self):
        return self.file_count

    def log_error(self, file_path):
        self.__errors.append(file_path)

    def log_ignored(self, file_path):
        self.__ignored.append(file_path)

    def dump(self):
        num_errors = len(self.__errors)
        if num_errors > 0:
            self.__logger.warn("%d files could not be read. Run with --version to see the full details."
                               % num_errors)
            self.__logger.debug("All errored files:\n" + pformat(self.__errors))

        num_ignored = len(self.__ignored)
        if num_ignored > 0:
            self.__logger.warn("%d files/directories were ignored. Run with --verbose to see the full details"
                               % num_ignored)
            self.__logger.debug("All ignored files/directories:\n" + pformat(self.__ignored))

        self.__logger.info("Results:\n" + pformat(self.__results))
