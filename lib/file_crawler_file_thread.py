import errno
import logging
import threading
from re import MULTILINE


class FileCrawlerFileThread(threading.Thread):
    def __init__(self, re, file_queue, results):
        threading.Thread.__init__(self)

        self.__re = re
        self.__file_queue = file_queue
        self.__results = results

    def run(self):
        while True:
            if not self.__file_queue.empty():
                file_path = self.__file_queue.get()
                self._check_file(file_path)
                self.__file_queue.task_done()

    def _check_file(self, file_path):
        logging.debug("Processing file %s" % file_path)
        try:
            fp = open(file_path)
        except IOError as e:
            # If there's a problem opening the file, we don't want to fail the entire request.
            if e.errno == errno.EACCES:
                logging.exception("Skipping {0} due to a permissions error".format(file_path))
            logging.exception("Unable to open {0}".format(file_path))
            self.__results.log_error(file_path)
        else:
            with fp:
                file_contents = fp.read()
                # Don't even have to bother manually iterating over each line individually, since
                # we can just do a multiline regex search. Using search() instead of match() here
                # because we want the regular expression to match any line in the file. So if the pattern starts with ^,
                # we want the file to match if ANY line matches, not just the first line.
                match = self.__re.search(file_contents, MULTILINE)

                if match:
                    logging.debug("Found match in {0}".format(file_path))

                self.__results.log_file(file_path, match)

        logging.debug("Done file processing %s" % file_path)
