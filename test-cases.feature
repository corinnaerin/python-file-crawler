Scenario: Executing file_crawler

Given an empty root_dir
Then an empty map should be returned

Given a root_dir without any subdirectories
And 10 total files
And 5 matching files
Then a map with a single key of that root_dir should be returned
And the value should be 5

Given a root_dir with a nested directory with a depth of 3
And 2 total files in each directory
And 1 matching file in each directory
Then a map with 4 keys should be returned
And the value of each key should be 1

Given a root_dir with 2 nested directories with a depth of 1
And 1 total file in each nested directory
And 1 matching file in each nested directory
And 1 total file in the root_dir
And 0 matching files in the root_dir
Then a map with 2 keys should be returns
And the value of the root_dir should be 0
And the value of the nested directory should be 1

Given a root_dir with a nested directory called 'node_modules'
And an exclude pattern of */node_modules/*
Then no files under /node_modules should be processed

Given a root_dir containing files with the extensions .html, .css, .js, .jsx, and .js.map
And an include pattern of *.js*
And an exclude pattern of *.map
Then all files with extensions .html, .css, .js.map should be ignored
And all files with .js and .jsx should be processed

Given a root_dir containing only binary files
Then the value of the root_dir should be 0

Given the --verbose flag
Then the log level should be increased from INFO to DEBUG

Given a huge root_dir (e.g. a node_modules) dir
Then a valid result should be returned without crashing or hanging

Given a root_dir with a symlink
Then the symlink should not be included in the results

Given a root_dir with a symlink
And the --follow-symlinks flag
Then the symlink should be included in the results

Given a root_dir with hidden files and directories
Then the hidden files and directories should not be included in the results

Given a root_dir with hidden files and directories
And the --include-hidden flag
Then the hidden files and directories should be included in the results

Given the --help flag
Then the program should not execute
And the help text should be displayed

Given no arguments
Then the program should exit with an error with the message "too few arguments"
And the basic help text should be displayed

Given an invalid root_dir
Then the program should exit with an error with the message "{root_dir} is not a valid directory"
And the basic help text should be displayed

Given an invalid regular expression
Then the program should exit with an error with the message "{keyword} is not a valid regular expression"
And the basic help text should be displayed

Given a root_dir with files without read access
Then the program should log an error for those files
And the remaining files/directories should be processed correctly