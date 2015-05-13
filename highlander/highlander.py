from logging import getLogger
from os import getcwd, unlink
from os.path import join, realpath, isfile

from psutil import Process, NoSuchProcess
from funcy import decorator

from .exceptions import InvalidPidFileError, PidFileExistsError

logger = getLogger(__name__)


@decorator
def one(call, pid_file=None):
    if not pid_file:
        pid_file = realpath(join(getcwd(), '.pid'))

    if _is_running(pid_file):
        exit(1)

    _set_running(pid_file)
    try:
        result = call()
    finally:
        _delete(pid_file)
    return result


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

    _delete(pid_file)
    return False


def _read_pid_file(filename):
    if not isfile(str(filename)):
        return None

    try:
        with open(filename, 'r') as f:
            pid, create_time = f.read().split()
        pid, create_time = int(pid), float(create_time)
    except ValueError:
        raise InvalidPidFileError()

    return pid, create_time


def _set_running(filename):
    if isfile(str(filename)):
        raise PidFileExistsError()

    p = Process()
    with open(filename, 'w') as f:
        f.write('{} {:.6f}'.format(p.pid, p.create_time()))


def _delete(filename):
    if not isfile(filename):
        raise InvalidPidFileError()
    unlink(filename)
