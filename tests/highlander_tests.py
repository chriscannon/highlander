from os import unlink
import shutil
from tempfile import mkstemp, mkdtemp
from unittest import TestCase, TestLoader, TestSuite, TextTestRunner
from os.path import isfile, realpath, join

from psutil import Process

from highlander import InvalidPidFileError, PidFileExistsError
from highlander.highlander import _read_pid_file, _delete, _set_running, _is_running
from highlander import one


class HighlanderTestCase(TestCase):
    def test_read_pid_no_file(self):
        self.assertRaises(InvalidPidFileError, _read_pid_file, None)

    def test_read_valid_pid_file(self):
        _, filename = mkstemp()
        try:
            with open(filename, 'w') as f:
                f.write('123 123.123456')
            pid, create_time = _read_pid_file(filename)
            self.assertEquals(123, pid)
            self.assertEquals(123.123456, create_time)
        finally:
            unlink(filename)

    def test_read_invalid_pid_file(self):
        _, filename = mkstemp()
        try:
            with open(filename, 'w') as f:
                f.write('abc def')
            self.assertRaises(InvalidPidFileError, _read_pid_file, filename)
        finally:
            unlink(filename)

    def test_read_empty_pid_file(self):
        _, filename = mkstemp()
        try:
            self.assertRaises(InvalidPidFileError, _read_pid_file, filename)
        finally:
            unlink(filename)

    def test_decorator(self):
        d = mkdtemp()
        pid_file = realpath(join(d, '.pid'))
        try:
            @one(pid_file)
            def f():
                print('hello')

            f()
        finally:
            shutil.rmtree(d)

    def test_delete_valid_file(self):
        _, f = mkstemp()
        try:
            _delete(f)
            self.assertFalse(isfile(f))
        finally:
            if isfile(f):
                unlink(f)

    def test_delete_invalid_file(self):
        self.assertRaises(InvalidPidFileError, _delete, 'not_a_file')

    def test_running_file_exists(self):
        _, f = mkstemp()
        try:
            self.assertRaises(PidFileExistsError, _set_running, f)
        finally:
            unlink(f)

    def test_running_valid_file(self):
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

    def test_invalid_file_is_running(self):
        self.assertFalse(_is_running(None))

    def test_no_process_is_running(self):
        _, f = mkstemp()
        try:
            with open(f, 'w') as pid_file:
                pid_file.write('99999999999 1.1')
            self.assertFalse(_is_running(f))
        finally:
            unlink(f)

    def test_valid_is_running(self):
        p = Process()
        _, f = mkstemp()
        try:
            with open(f, 'w') as pid_file:
                pid_file.write('{0} {1:6f}'.format(p.pid, p.create_time()))
            self.assertTrue(_is_running(f))
        finally:
            unlink(f)

    def test_create_time_mismatch_is_running(self):
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

    def test_process_is_running(self):
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


def get_suite():
    loader = TestLoader()
    suite = TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(HighlanderTestCase))
    return suite


if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(get_suite())
