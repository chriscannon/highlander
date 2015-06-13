# Highlander: There can only be one...
[![Build Status](https://travis-ci.org/chriscannon/highlander.svg?branch=master)](https://travis-ci.org/chriscannon/highlander)
[![Coverage Status](https://coveralls.io/repos/chriscannon/highlander/badge.svg)](https://coveralls.io/r/chriscannon/highlander)

About
=====
Highlander is a decorator to help developers ensure that their python 
process is only running once. This is helpful when you have
a python program running on a set schedule (i.e., a cron) and you do
not want one run of the program to overlap with another run. Highlander
accomplishes this by creating a file on disk that contains the current
process identifier (PID) and creation time. If Highlander detects that
a PID file currently exists it reads the PID and creation time from the
file, checks to see if it exists. If it does exist, it ends the program
and logs that the program was already running. If it does not exist,
Highlander removes the old process information file, creates a new one, and
executes the function associated with the decorator.


Installation
============
    pip install highlander-one
  

Examples
========
    from highlander import one
    
    @one # Create a PID file in the current working directory.
    def long_running_operation():
        ...
        
        
    from highlander import one
    
    @one('/tmp/pid_file') # Create a PID file in a user-specified directory.
    def long_running_operation():
        ...
