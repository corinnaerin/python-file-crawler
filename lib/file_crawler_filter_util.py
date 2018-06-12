import logging
from fnmatch import fnmatch
from os.path import join

from binaryornot.check import is_binary

logger = logging.getLogger('file_crawler.file_crawler_filter_util')


# checks whether the file / directory should be excluded from computation
def __should_exclude(cli_args, name, full_path, is_file, results):
    exclude = False

    if not is_file and results and results.has_directory(full_path):
        logger.warn("Already processed %s, most likely due to an infinite loop of symbolic links" % full_path)
        exclude = True

    elif not cli_args.include_hidden and name.startswith('.'):
        logger.debug("Ignoring hidden file/directory {0}".format(full_path))
        exclude = True

    elif is_file:
        if is_binary(full_path):
            logger.debug("Ignoring binary file {0}".format(full_path))
            exclude = True

        if cli_args.include and not fnmatch(full_path, cli_args.include):
            logger.debug("Ignoring file {0} that does not match include glob".format(full_path))
            exclude = True

        elif cli_args.exclude and fnmatch(full_path, cli_args.exclude):
            logger.debug("Ignoring file {0} that matches exclude glob".format(full_path))
            exclude = True

    if exclude:
        results.log_ignored(full_path)

    return exclude


def exclude_generator(cli_args, current_dir, names, is_file, results):
    for name in names:
        full_path = join(current_dir, name)
        if not __should_exclude(cli_args, name, full_path, is_file, results):
            yield full_path


def filter_excluded_in_place(cli_args, current_dir, names, is_file, results):
    # Unfortunately walk() requires that the dirs list MUST be modified in place
    # If we use list comprehension to create a new list and overwrite the existing
    # variable, it won't actually skip these values
    for i in reversed(range(len(names))):
        full_path = join(current_dir, names[i])
        if __should_exclude(cli_args, names[i], full_path, is_file, results):
            del names[i]
