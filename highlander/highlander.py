from logging import getLogger
from os import getcwd, unlink
from os.path import join, realpath, isfile

from psutil import Process, NoSuchProcess
from funcy import decorator

from .exceptions import InvalidPidFileError, PidFileExistsError

logger = getLogger(__name__)
default_location = realpath(join(getcwd(), '.pid'))


@decorator
def one(call, pid_file=default_location):
    if _is_running(pid_file):
        logger.info('The process is already running.')
        return

    _set_running(pid_file)
    try:
        result = call()
    finally:
        _delete(pid_file)
    return result


def _is_running(pid_file):
    if not isfile(str(pid_file)):
        return False

    pid, create_time = _read_pid_file(pid_file)

    try:
        current = Process(pid)
    except NoSuchProcess:
        return False

    if current.create_time() == create_time:
        return True

    _delete(pid_file)
    return False


def _read_pid_file(filename):
    if not isfile(str(filename)):
        raise InvalidPidFileError()

    try:
        with open(filename, 'r') as f:
            pid, create_time = f.read().split()
        return int(pid), float(create_time)
    except ValueError:
        raise InvalidPidFileError()


def _set_running(filename):
    if isfile(str(filename)):
        raise PidFileExistsError()

    p = Process()
    with open(filename, 'w') as f:
        f.write('{0} {1:.6f}'.format(p.pid, p.create_time()))


def _delete(filename):
    if not isfile(filename):
        raise InvalidPidFileError()
    unlink(filename)
