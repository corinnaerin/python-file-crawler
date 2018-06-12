import logging

from file_crawler_filter_util import exclude_generator

logger = logging.getLogger('file_crawler.' + __name__)


def dir_worker(cli_args, dir_queue, file_queue, results):
    while True:
        if not dir_queue.empty():
            directory = dir_queue.get()
            _add_files_to_queue(cli_args, directory, file_queue, results)
            dir_queue.task_done()


def _add_files_to_queue(cli_args, directory, file_queue, results):
    dir_name = directory['dir_name']
    files = directory['files']
    logger.debug("Processing directory %s" % dir_name)

    for file_path in exclude_generator(cli_args, dir_name, files, True, results):
        file_queue.put(file_path)

    logger.debug("Done adding %d files in directory %s" % (len(files), dir_name))
