import logging
from os import walk

from file_crawler_args import FileCrawlerArgs
from file_crawler_dir_thread import FileCrawlerDirThread
from file_crawler_file_thread import FileCrawlerFileThread
from file_crawler_inputs import FileCrawlerInputs
from file_crawler_results import FileCrawlerResults
from timer import Timer

MAX_THREADS = 30
LOGGING_FORMAT = '%(asctime)s [%(levelname)s] [%(name)s] [%(threadName)s] %(message)s'


class FileCrawler:
    def __init__(self):

        self.__cli_args = FileCrawlerArgs().args

        # Create our logging instance
        logging_level = logging.INFO
        if self.__cli_args.verbose:
            logging_level = logging.DEBUG
        logging.basicConfig(level=logging_level,
                            format=LOGGING_FORMAT)

        self.__timer = Timer(start_message="Starting to scan %s for files matching %s" %
                                           (self.__cli_args.root_dir, self.__cli_args.keyword.pattern))

        self.results = FileCrawlerResults()
        self.threads = []
        self.__inputs = FileCrawlerInputs(self.__cli_args)

        self._create_threads()

    # Returns an object hash from directory name to the number of files that match the keyword
    def get_results(self):

        # Recursively walk through all of the files & directories in the root
        logging.debug("Starting to fill the queue with all of the files")

        for current_dir, dirs, files in walk(self.__cli_args.root_dir, followlinks=self.__cli_args.follow_symlinks):
            self.results.add_directory(current_dir)

            self.__inputs.dir_queue.put({
                'dir_name': current_dir,
                'files': files
            })

            # Filter out directories that should be excluded from processing
            # It's a bit confusing, because dirs is not just a block-scoped value containing the directories
            # in the current directory. It's also used by walk() to continue recursing. So you can remove
            # directories from the list to prevent it from stepping into them. But it does make for a call pattern
            # that's somewhat difficult to follow
            self.__inputs.filter_hidden_dirs(current_dir, dirs, self.results)

        # Wait for all files in the queue to be processed
        self.__inputs.file_queue.join()
        self.__inputs.dir_queue.join()

        self.results.dump()
        self.__timer.stop("Finished scanning %d files" % self.results.file_count)
        logging.shutdown()
        return self.results

    def _create_threads(self):
        for i in range(MAX_THREADS / 2):
            file_thread = FileCrawlerFileThread(self.__cli_args.keyword, self.__inputs.file_queue, self.results)
            file_thread.daemon = True
            file_thread.start()
            self.threads.append(file_thread)
            dir_thread = FileCrawlerDirThread(self.__inputs, self.results)
            dir_thread.daemon = True
            dir_thread.start()


file_crawler = FileCrawler()
results = file_crawler.get_results()
