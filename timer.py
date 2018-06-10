from time import time
import logging


class Timer:
    def __init__(self, log_level=logging.INFO, start_message=None):
        self.start_time = time()
        self.log_level = log_level
        if start_message:
            logging.log(self.log_level, start_message)

    def stop(self, message):
        end_time = time()
        run_time = end_time - self.start_time
        logging.log(self.log_level, "%s in %d ms (%.2f s)" % (message, run_time * 1000, run_time))

