import logging


class FileCrawlerBase:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        log_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] %(message)s')
        log_handler.setFormatter(formatter)
        self.logger.addHandler(log_handler)
