from functools import wraps
from logging import getLogger
from os import getcwd, unlink
from os.path import join, realpath, isfile
import pickle

from psutil import Process


logger = getLogger(__name__)


def one(f):
    @wraps(f)
    def decorator():
        pid_file = realpath(join(getcwd(), '.pid'))
        _set_running(pid_file)

    return decorator


def _is_running():
    pass


def _read_pid_file(filename):
    with open(filename, 'r') as f:
        pid, create_time = f.read().split(',')
    return Process(int(pid))


def _set_running(filename):
    p = Process()
    with open(filename, 'w') as f:
        f.write('{},{}'.format(p.pid, p.create_time()))


def _unlink_pid_file(f):
    unlink(f)
