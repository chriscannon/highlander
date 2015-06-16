class InvalidPidFileError(Exception):
    """ An exception when an invalid PID file is read."""

class PidFileExistsError(Exception):
    """ An exception when a PID file already exists."""
