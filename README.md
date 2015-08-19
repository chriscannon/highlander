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
on disk that contains the current process identifier (PID) and
creation time. If Highlander detects that the PID directory currently
exists it reads the PID file inside it for the PID and creation time
and checks to see if that process exists. If it does exist, it ends the program
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

    @one('/tmp/my_app/.pid')
    def run():
        ...

    if __name__ == '__main__':
        run()
        
F.A.Q.
======
**Why not use flock? Stop reinventing Unix dumb dumb!**

There are three reasons I did not use flock:

1. I knew there was no way that `fcntl.flock` would work the same on all operating systems
and I found a lot of articles on the web stating just that.
What I use in its stead is directory creation, which I believe is a much
more reliable way to do locking across all operating systems and still
only dependent on the file system to ensure it's atomic.

2. If a process is killed abruptly (e.g., kill -9) with flock the file
remains exclusively locked even though the process is not running. This
occurs because the process did not have enough time to clean up the exclusive handle on the lock file. What
this means is that when you attempt to run your program it will be unable to
acquire the lock and your program will not run until you manually intervene and
delete the lock file. My solution does not have this problem.

3. If you are using the flock Unix tool in conjuction with your program its
default behavior is to hang until the lock file is free and then execute the command.
In my opinion, this is not ideal default behaviour because you could have a ton of
processes build up over time and waste resources. What Highlander does is essentially skip
that run of the program by returning immediately.
