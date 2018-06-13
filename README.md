usage: file_crawler.py [-h] [-d] [-f] [-v] [-i INCLUDE] [-e EXCLUDE]
                       root_dir keyword

Search directory for matching files. NOTE: file patterns are not regular
expressions or globs. They are Unix shell-style wildcards that will be matched
against the absolute path of the file (even if you specified a relative
root_dir path). See https://docs.python.org/2.7/library/fnmatch.html for
details.

positional arguments:
  root_dir              root directory to search
  keyword               keyword (regular expression) to search for

optional arguments:
  -h, --help            show this help message and exit
  -d, --include-hidden  whether to include hidden files & directories.
                        defaults to False.
  -f, --follow-symlinks
                        whether to follow symlinks. defaults to False.
  -v, --verbose         whether to decrease the log level from INFO to info.
                        defaults to False.
  -i INCLUDE, --include INCLUDE
                        pattern for files & directories that should be
                        included. If specified, nothing that doesn't match
                        this pattern will be included.
  -e EXCLUDE, --exclude EXCLUDE
                        pattern for files & directories that should be
                        excluded. Can be used in conjunction with --include to
                        narrow down further.
