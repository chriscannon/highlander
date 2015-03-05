from unittest import TestCase
from highlander.highlander import _read_pid_file


class HighlanderTests(TestCase):
    def read_pid_no_file_test(self):
        self.assertFalse(_read_pid_file(None))
