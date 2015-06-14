from os import unlink, mkdir
from tempfile import mkstemp, mkdtemp
from unittest import TestCase, TestLoader, TestSuite, TextTestRunner
from os.path import isfile, realpath, join, isdir
from shutil import rmtree

from psutil import Process

from highlander import InvalidPidFileError, PidFileExistsError, InvalidPidDirectoryError
from highlander.highlander import _read_pid_file, _delete, _set_running, _is_running, _get_pid_filename
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
        _, f = mkstemp()
        try:
            self.assertRaises(InvalidPidFileError, _read_pid_file, f)
        finally:
            unlink(f)

    def test_decorator(self):
        d = mkdtemp()
        pid_directory = realpath(join(d, '.pid'))
        try:
            @one(pid_directory)
            def f():
                return True

            self.assertTrue(f())
        finally:
            rmtree(d)

    def test_delete_valid_directory(self):
        d = mkdtemp()
        try:
            _delete(d)
            self.assertFalse(isdir(d))
        finally:
            if isdir(d):
                rmtree(d)

    def test_delete_invalid_directory(self):
        self.assertRaises(InvalidPidDirectoryError, _delete, 'not_a_directory')

    def test_running_file_exists(self):
        d = mkdtemp()
        f = open(join(d, 'INFO'), 'w')
        f.close()

        try:
            self.assertRaises(PidFileExistsError, _set_running, d)
        finally:
            rmtree(d)

    def test_running_valid_file(self):
        temp_d = mkdtemp()
        d = realpath(join(temp_d, '.pid'))
        mkdir(d)

        try:
            _set_running(d)
            with open(join(d, 'INFO'), 'r') as pid_file:
                process_info = pid_file.read().split()
            p = Process()
            self.assertEquals(p.pid, int(process_info[0]))
            self.assertEquals(p.create_time(), float(process_info[1]))
        finally:
            rmtree(temp_d)

    def test_no_process_is_running(self):
        d = mkdtemp()
        f = _get_pid_filename(d)
        try:
            with open(f, 'w') as pid_file:
                pid_file.write('99999999999 1.1')
            self.assertFalse(_is_running(d))
        finally:
            rmtree(d)

    def test_valid_is_running(self):
        p = Process()
        d = mkdtemp()
        f = _get_pid_filename(d)
        try:
            with open(f, 'w') as pid_file:
                pid_file.write('{0} {1:6f}'.format(p.pid, p.create_time()))
            self.assertTrue(_is_running(d))
        finally:
            rmtree(d)

    def test_create_time_mismatch_is_running(self):
        p = Process()
        d = mkdtemp()
        f = _get_pid_filename(d)
        try:
            with open(f, 'w') as pid_file:
                pid_file.write('{0} 1.1'.format(p.pid))
            self.assertFalse(_is_running(d))
            self.assertFalse(isfile(f))
            self.assertFalse(isdir(d))
        finally:
            if isdir(d):
                rmtree(d)

    def test_process_is_running(self):
        d = mkdtemp()
        pid_directory = realpath(join(d, '.pid'))
        try:
            @one(pid_directory)
            def f1():
                return f2()

            @one(pid_directory)
            def f2():
                return True

            self.assertIsNone(f1())
        finally:
            rmtree(d)

    def test_get_pid_filename(self):
        self.assertEquals('/test/INFO', _get_pid_filename('/test'))

    def test_other_os_error(self):
        self.assertRaises(OSError, _is_running, '/')


def get_suite():
    loader = TestLoader()
    suite = TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(HighlanderTestCase))
    return suite


if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(get_suite())
