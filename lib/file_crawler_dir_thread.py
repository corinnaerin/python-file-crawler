import logging
import threading


class FileCrawlerDirThread(threading.Thread):
    def __init__(self, inputs, results):
        threading.Thread.__init__(self)
        self.__inputs = inputs
        self.__results = results

    def run(self):
        while True:
            if not self.__inputs.dir_queue.empty():
                directory = self.__inputs.dir_queue.get()
                self._check_files_in_dir(directory)
                self.__inputs.dir_queue.task_done()

    def _check_files_in_dir(self, directory):
        logging.debug("Processing directory %s" % directory['dir_name'])
        self.__inputs.add_files_to_queue(directory['dir_name'], directory['files'], self.__results)
        logging.debug("Done processing %d files in directory %s" % (len(directory['files']), directory['dir_name']))
