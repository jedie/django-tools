import tempfile
import unittest
from pathlib import Path

from django_tools.unittest_utils.isolated_filesystem import isolated_filesystem
from django_tools.unittest_utils.unittest_base import BaseUnittestCase


class TestIsolatedFilesystem(BaseUnittestCase):

    def setUp(self):
        super().setUp()
        self.old_cwd = Path().cwd()

        # set in self.assert_in_isolated_filesystem()
        self.temp_cwd = None
        self.temp_file = None

    def assert_in_isolated_filesystem(self, prefix=None):
        self.temp_cwd = Path().cwd()
        print(self.temp_cwd)
        self.assertNotEqual(self.temp_cwd, self.old_cwd)

        temp_dir = tempfile.gettempdir()
        self.assert_startswith(str(self.temp_cwd), temp_dir)

        if prefix is not None:
            reference = Path(temp_dir, prefix)
            self.assert_startswith(str(self.temp_cwd), str(reference))

        self.temp_file = Path(self.temp_cwd, "test_file.txt")

        with self.temp_file.open("w") as f:
            f.write(prefix or "no prefix")

        self.assertTrue(self.temp_file.is_file())

    def assert_after(self):
        self.assertTrue(self.temp_cwd is not None, "ERROR: 'self.assert_in_isolated_filesystem()' not called?!?")
        self.assertFalse(self.temp_cwd.is_dir(), "ERROR: %r still exists?!?" % self.temp_cwd)
        self.assertFalse(self.temp_file.is_file(), "ERROR: %r still exists!" % self.temp_file)

    def test_as_context_manager(self):
        prefix="test_as_context_manager"
        with isolated_filesystem(prefix=prefix):
            self.assert_in_isolated_filesystem(prefix)

        self.assert_after()

    def test_as_func_decotator(self):

        @isolated_filesystem()
        def in_isolated_filesystem():
            self.assert_in_isolated_filesystem(prefix="in_isolated_filesystem")

        in_isolated_filesystem()
        self.assert_after()

    def test_as_class_decotator(self):

        @isolated_filesystem()
        class InIsolatedFilesystem(unittest.TestCase):
            def call_assert_in_isolated_filesystem(self, parent):
                parent.assert_in_isolated_filesystem(prefix="InIsolatedFilesystem")

        test_case = InIsolatedFilesystem()
        test_case.setUp()
        test_case.call_assert_in_isolated_filesystem(parent=self)
        test_case.tearDown()

        self.assert_after()
