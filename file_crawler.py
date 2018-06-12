import logging
from multiprocessing import freeze_support
from multiprocessing.managers import SyncManager
from os import walk

from lib.file_crawler_args import get_cli_args
from lib.file_crawler_dir_process import FileCrawlerDirProcess
from lib.file_crawler_file_process import FileCrawlerFileProcess
from lib.file_crawler_filter_util import filter_excluded_in_place
from lib.file_crawler_results import FileCrawlerResults
from lib.timer import Timer

MAX_PROCESSES = 30
LOGGING_FORMAT = '%(asctime)s [%(levelname)s] [%(processName)s] %(message)s'


class FileCrawlerManager(SyncManager):
    pass


FileCrawlerManager.register('FileCrawlerResults', FileCrawlerResults)


class FileCrawler:

    def __init__(self):
        if __name__ == '__main__':
            # For Windows support
            freeze_support()

            # Create logger
            self.__logger = logging.getLogger('file_crawler')
            self.__logger.setLevel(logging.INFO)
            logging_handler = logging.StreamHandler()
            logging_formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(processName)s] %(message)s')
            logging_handler.setFormatter(logging_formatter)
            self.__logger.addHandler(logging_handler)

            self.__manager = FileCrawlerManager()
            self.__manager.start()

            # Create process-safe args object
            self.__cli_args = get_cli_args(self.__manager)

            if self.__cli_args.verbose:
                self.__logger.setLevel(logging.DEBUG)

            self.__timer = Timer(start_message="Starting to scan %s for files matching %s" %
                                               (self.__cli_args.root_dir, self.__cli_args.keyword.pattern))

            self.__dir_queue = self.__manager.Queue()
            self.__file_queue = self.__manager.Queue()

            self.__results = self.__manager.FileCrawlerResults(self.__logger.getEffectiveLevel())

            self.__processes = list()
            self._create_processes()

    # Returns an object hash from directory name to the number of files that match the keyword
    def get_results(self):

        self._fill_dir_queue()

        # Wait for all files & directories in the queues to be processed
        self.__dir_queue.join()
        self.__file_queue.join()

        for process in self.__processes:
            process.terminate()

        self.__results.dump()
        self.__timer.stop("Finished scanning %d files" % self.__results.get_file_count())
        return self.__results

    def _fill_dir_queue(self):
        # Recursively walk through all of the files & directories in the root
        self.__logger.debug("Starting to fill the queue with all of the directories")

        for current_dir, dirs, files in walk(self.__cli_args.root_dir, followlinks=self.__cli_args.follow_symlinks):
            self.__logger.debug("Adding directory %s" % current_dir)

            self.__results.add_directory(current_dir)
            self.__dir_queue.put({
                'dir_name': current_dir,
                'files': files
            })

            # Filter out directories that should be excluded from processing
            # It's a bit confusing, because dirs is not just a block-scoped value containing the directories
            # in the current directory. It's also used by walk() to continue recursing. So you can remove
            # directories from the list to prevent it from stepping into them. But it does make for a call pattern
            # that's somewhat difficult to follow
            filter_excluded_in_place(self.__cli_args, current_dir, dirs, False, self.__results)

    def _create_processes(self):
        for i in range(MAX_PROCESSES / 2):
            file_process = FileCrawlerFileProcess(self.__cli_args.keyword, self.__file_queue, self.__results)
            file_process.start()
            self.__processes.append(file_process)

            dir_process = FileCrawlerDirProcess(self.__cli_args, self.__dir_queue,
                                                self.__file_queue, self.__results)
            dir_process.start()
            self.__processes.append(dir_process)


file_crawler = FileCrawler()
results = file_crawler.get_results()
