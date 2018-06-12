import errno
import logging
from re import MULTILINE

logger = logging.getLogger('file_crawler.' + __name__)


def file_worker(re, file_queue, results):
    while True:
        if not file_queue.empty():
            file_path = file_queue.get()
            _check_file(re, file_path, results)
            file_queue.task_done()


def _check_file(re, file_path, results):
    logging.debug("Processing file %s" % file_path)
    try:
        fp = open(file_path)

    except IOError as e:
        # If there's a problem opening the file, we don't want to fail the entire request.
        if e.errno == errno.EACCES:
            logger.exception("Skipping %s due to a permissions error" % file_path)
        logger.exception("Unable to open %s" % file_path)
        results.log_error(file_path)

    else:
        with fp:

            file_contents = fp.read()
            # Don't even have to bother manually iterating over each line individually, since
            # we can just do a multiline regex search. Using search() instead of match() here
            # because we want the regular expression to match any line in the file. So if the pattern starts with ^,
            # we want the file to match if ANY line matches, not just the first line.
            match = re.search(file_contents, MULTILINE)

            if match:
                logger.debug("Found match in {0}".format(file_path))
                results.log_match(file_path)

            results.increment_counter()

        logger.debug("Done processing file %s" % file_path)
