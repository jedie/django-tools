import tempfile
from pathlib import Path
from unittest import TestCase

from django_tools.unittest_utils import assertments
from django_tools.unittest_utils.isolated_filesystem import isolated_filesystem


CWD = Path().cwd()


class TestIsolatedFilesystem(TestCase):

    def setUp(self):
        super().setUp()

        # set in self.assert_in_isolated_filesystem()
        self.temp_cwd = None
        self.temp_file = None

    def assert_in_isolated_filesystem(self, prefix=None):
        self.temp_cwd = Path().cwd()
        self.assertNotEqual(self.temp_cwd, CWD)

        temp_dir = tempfile.gettempdir()
        assertments.assert_startswith(str(self.temp_cwd), temp_dir)

        if prefix is not None:
            reference = Path(temp_dir, prefix)
            assertments.assert_startswith(str(self.temp_cwd), str(reference))

        self.temp_file = Path(self.temp_cwd, "test_file.txt")

        with self.temp_file.open("w") as f:
            f.write(prefix or "no prefix")

        self.assertTrue(self.temp_file.is_file())

    def assert_after(self):
        self.assertTrue(self.temp_cwd is not None, "ERROR: 'self.assert_in_isolated_filesystem()' not called?!?")
        self.assertFalse(self.temp_cwd.is_dir(), f"ERROR: {self.temp_cwd!r} still exists?!?")
        self.assertFalse(self.temp_file.is_file(), f"ERROR: {self.temp_file!r} still exists!")

    def test_as_context_manager(self):
        prefix = "test_as_context_manager"
        with isolated_filesystem(prefix=prefix):
            self.assert_in_isolated_filesystem(prefix)

        self.assert_after()

    def test_as_func_decotator(self):

        @isolated_filesystem()
        def in_isolated_filesystem():
            self.assert_in_isolated_filesystem(prefix="in_isolated_filesystem")

        in_isolated_filesystem()
        self.assert_after()
