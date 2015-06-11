from os import unlink
import shutil
from tempfile import mkstemp, mkdtemp
from unittest import TestCase
from os.path import isfile, realpath, join

from psutil import Process

from highlander import InvalidPidFileError, PidFileExistsError
from highlander.highlander import _read_pid_file, _delete, _set_running, _is_running
from highlander import one


class HighlanderTests(TestCase):
    def read_pid_no_file_test(self):
        self.assertRaises(InvalidPidFileError, _read_pid_file, None)

    def read_valid_pid_file_test(self):
        _, filename = mkstemp()
        try:
            with open(filename, 'w') as f:
                f.write('123 123.123456')
            pid, create_time = _read_pid_file(filename)
            self.assertEquals(123, pid)
            self.assertEquals(123.123456, create_time)
        finally:
            unlink(filename)

    def read_invalid_pid_file_test(self):
        _, filename = mkstemp()
        try:
            with open(filename, 'w') as f:
                f.write('abc def')
            self.assertRaises(InvalidPidFileError, _read_pid_file, filename)
        finally:
            unlink(filename)

    def read_empty_pid_file_test(self):
        _, filename = mkstemp()
        try:
            self.assertRaises(InvalidPidFileError, _read_pid_file, filename)
        finally:
            unlink(filename)

    def decorator_test(self):
        d = mkdtemp()
        pid_file = realpath(join(d, '.pid'))
        try:
            @one(pid_file)
            def f():
                print('hello')
            f()
        finally:
            shutil.rmtree(d)

    def delete_valid_file_test(self):
        _, f = mkstemp()
        try:
            _delete(f)
            self.assertFalse(isfile(f))
        finally:
            if isfile(f):
                unlink(f)

    def delete_invalid_file_test(self):
        self.assertRaises(InvalidPidFileError, _delete, 'not_a_file')

    def running_file_exists_test(self):
        _, f = mkstemp()
        try:
            self.assertRaises(PidFileExistsError, _set_running, f)
        finally:
            unlink(f)

    def running_valid_file_test(self):
        d = mkdtemp()
        f = realpath(join(d, '.pid'))
        try:
            _set_running(f)
            with open(f, 'r') as pid_file:
                process_info = pid_file.read().split()
            p = Process()
            self.assertEquals(p.pid, int(process_info[0]))
            self.assertEquals(p.create_time(), float(process_info[1]))
        finally:
            shutil.rmtree(d)

    def invalid_file_is_running_test(self):
        self.assertFalse(_is_running(None))

    def no_process_is_running_test(self):
        _, f = mkstemp()
        try:
            with open(f, 'w') as pid_file:
                pid_file.write('99999999999 1.1')
            self.assertFalse(_is_running(f))
        finally:
            unlink(f)

    def valid_is_running_test(self):
        p = Process()
        _, f = mkstemp()
        try:
            with open(f, 'w') as pid_file:
                pid_file.write('{0} {1:6f}'.format(p.pid, p.create_time()))
            self.assertTrue(_is_running(f))
        finally:
            unlink(f)

    def create_time_mismatch_is_running_test(self):
        p = Process()
        _, f = mkstemp()
        try:
            with open(f, 'w') as pid_file:
                pid_file.write('{0} 1.1'.format(p.pid))
            self.assertFalse(_is_running(f))
            self.assertFalse(isfile(f))
        finally:
            if isfile(f):
                unlink(f)

    def process_is_running_test(self):
        d = mkdtemp()
        pid_file = realpath(join(d, '.pid'))
        try:
            @one(pid_file)
            def f1():
                f2()

            @one(pid_file)
            def f2():
                print('hello')

            f1()
        finally:
            shutil.rmtree(d)
