from functools import wraps
from logging import getLogger
from os import getcwd, unlink
from os.path import join, realpath, isfile

from psutil import Process, NoSuchProcess


logger = getLogger(__name__)


def one(f):
    @wraps(f)
    def decorator():
        pid_file = realpath(join(getcwd(), '.pid'))
        if _is_running(pid_file):
            exit(0)
        _set_running(pid_file)
        try:
            f()
        finally:
            unlink(pid_file)

    return decorator


def _is_running(pid_file):
    previous = _read_pid_file(pid_file)

    if previous is None:
        return False

    try:
        current = Process(previous[0])
    except NoSuchProcess:
        return False

    if current.create_time() == previous[1]:
        return True

    unlink(pid_file)
    return False


def _read_pid_file(filename):
    if not isfile(str(filename)):
        return None

    with open(filename, 'r') as f:
        pid, create_time = f.read().split(',')
    return int(pid), float(create_time)


def _set_running(filename):
    if isfile(str(filename)):
        raise Exception('PID file already exists.')

    p = Process()
    with open(filename, 'w') as f:
        f.write('{},{}'.format(p.pid, p.create_time()))
