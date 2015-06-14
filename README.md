# Highlander: There can be only one...
[![Build Status](https://travis-ci.org/chriscannon/highlander.svg?branch=master)](https://travis-ci.org/chriscannon/highlander)
[![Coverage Status](https://coveralls.io/repos/chriscannon/highlander/badge.svg)](https://coveralls.io/r/chriscannon/highlander)

About
=====
Highlander is a decorator to help developers ensure that their python 
process is only running once. This is helpful when you have
a python program running on a set schedule (i.e., a cron) and you do
not want one run of the program to overlap with another run. Highlander
accomplishes this by creating a directory containing a file
on disk that contains the current
process identifier (PID) and creation time. If Highlander detects that
the PID directory currently exists it reads the PID file inside
it for the PID and creation time and checks to see if that process exists.
If it does exist, it ends the program
and logs that the program was already running. If it does not exist,
Highlander removes the old process information directory and file, creates new ones, and
executes the function associated with the decorator.


Installation
============
    pip install highlander-one
  

Examples
========
An example using the default directory (i.e., current working directory):

    from highlander import one
    
    @one()
    def run():
        ...
        
    if __name__ == '__main__':
        run()
      
An example using a user-specified directory:

    from highlander import one
    
    @one('/tmp/.pid')
    def run():
        ...
        
    if __name__ == '__main__':
        run()

TODO
====
* Add an argument to specify a timeout.
