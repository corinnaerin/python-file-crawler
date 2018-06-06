import os

from file_crawler_args import FileCrawlerArgs
from file_crawler_base import FileCrawlerBase


class FileCrawler(FileCrawlerBase):
    def __init__(self):
        FileCrawlerBase.__init__(self, __name__)
        self.args = FileCrawlerArgs().args
        print self.args
        self.process_files()

    def files_generator(self, names):
        for name in names:
            if (not self.args.include_hidden) and name.startswith('.'):
                self.logger.debug("Ignoring hidden file {0}".format(name))
            else:
                yield name

    def filter_hidden_dirs(self, names):
        for name in names:
            if (not self.args.include_hidden) and name.startswith('.'):
                self.logger.debug("Ignoring hidden directory {0}".format(name))
                names.remove(name)

    def process_files(self):
        for root, dirs, files in os.walk(self.args.root_dir, followlinks=self.args.follow_symlinks):
            for fileName in self.files_generator(files):
                self.logger.info("Processing {0}".format(fileName))
            self.filter_hidden_dirs(dirs)


FileCrawler()
