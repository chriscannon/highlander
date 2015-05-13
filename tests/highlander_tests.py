from os import unlink
import shutil
from tempfile import mkstemp, mkdtemp
from unittest import TestCase
from os.path import isfile, realpath, join
from psutil import Process
from highlander import InvalidPidFileError, PidFileExistsError

from highlander.highlander import _read_pid_file, _delete, _set_running
from highlander import one


class HighlanderTests(TestCase):
    def read_pid_no_file_test(self):
        self.assertFalse(_read_pid_file(None))

    def read_valid_pid_file_test(self):
        _, filename = mkstemp()
        try:
            with open(filename, 'w') as f:
                f.write('123 123.12')
            pid, create_time = _read_pid_file(filename)
            self.assertEquals(123, pid)
            self.assertEquals(123.12, create_time)
        finally:
            unlink(filename)

    def read_invalid_pid_file_test(self):
        _, filename = mkstemp()
        with open(filename, 'w') as f:
            f.write('abc def')
        self.assertRaises(InvalidPidFileError, _read_pid_file, filename)
        unlink(filename)

    def read_empty_pid_file_test(self):
        _, filename = mkstemp()
        self.assertRaises(InvalidPidFileError, _read_pid_file, filename)
        unlink(filename)

    def decorator_test(self):
        d = mkdtemp()
        pid_file = realpath(join(d, '.pid'))
        @one(pid_file)
        def f():
            print 'hello'
        f()
        shutil.rmtree(d)

    def delete_valid_file_test(self):
        _, f = mkstemp()
        _delete(f)
        self.assertFalse(isfile(f))

    def delete_invalid_file_test(self):
        self.assertRaises(InvalidPidFileError, _delete, 'not_a_file')

    def running_file_exists_test(self):
        _, f = mkstemp()
        self.assertRaises(PidFileExistsError, _set_running, f)

    def running_valid_file_test(self):
        d = mkdtemp()
        f = realpath(join(d, '.pid'))
        _set_running(f)
        with open(f, 'r') as pid_file:
            process_info = pid_file.read().split()
        p = Process()
        self.assertEquals(p.pid, int(process_info[0]))
        self.assertEquals(p.create_time(), float(process_info[1]))
        shutil.rmtree(d)
