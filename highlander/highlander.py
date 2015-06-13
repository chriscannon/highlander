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
    """ Check if the call is already running. If so, bail out. If not, create a
    file that contains the process identifier (PID) and creation time. After call
    has completed, remove the process information file.
    :param call: The original function using the @one decorator.
    :param pid_file: The name of the file where the process information will be written.
    :return: The output of the original function.
    """
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
    """ Determine whether or not the process is currently running.
    :param pid_file: The PID file containing the process information.
    :return: Whether or not the process is currently running.
    """
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
    """Read the current process information from disk.
    :param filename: The name of the file containing the process information.
    :return: The PID and creation time of the current running process.
    """
    if not isfile(str(filename)):
        raise InvalidPidFileError()

    try:
        with open(filename, 'r') as f:
            pid, create_time = f.read().split()
        return int(pid), float(create_time)
    except ValueError:
        raise InvalidPidFileError()


def _set_running(filename):
    """Write the current process information to disk.
    :param filename: The name of the file where the process information will be written.
    """
    if isfile(str(filename)):
        raise PidFileExistsError()

    p = Process()
    with open(filename, 'w') as f:
        f.write('{0} {1:.6f}'.format(p.pid, p.create_time()))


def _delete(filename):
    """Delete a file on disk.
    :param filename: The name of the file to be deleted.
    """
    if not isfile(str(filename)):
        raise InvalidPidFileError()
    unlink(filename)
