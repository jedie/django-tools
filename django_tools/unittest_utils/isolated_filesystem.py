import logging
import os
import shutil
import tempfile
from pathlib import Path

from django.test.utils import TestContextDecorator

from django_tools.unittest_utils.assertments import assert_is_dir


logger = logging.getLogger(__name__)


class isolated_filesystem(TestContextDecorator):
    """
    Acts as either a decorator or a context manager.

    with isolated_filesystem(prefix="temp_dir_prefix"):
        print("I'm in the temp path here: %s" % Path().cwd())

    or:

    class FooBarTestCase(TestCase):
        @isolated_filesystem()
        def test_foo(self):
            print("I'm in the temp path here: %s" % Path().cwd())
    """

    def __init__(self, prefix=None):
        super().__init__()

        self.prefix = prefix
        self.prefix_candidate = None
        self.cwd = None
        self.temp_path = None

    def enable(self):
        if self.prefix is None:
            prefix = self.prefix_candidate
        else:
            prefix = self.prefix

        print(f"Use prefix: {prefix!r}")

        self.cwd = Path().cwd()
        self.temp_path = tempfile.mkdtemp(prefix=prefix)
        os.chdir(self.temp_path)

    def disable(self):
        print(f'Delete: {self.temp_path}')
        os.chdir(str(self.cwd))  # str() needed for older python <=3.5
        try:
            shutil.rmtree(self.temp_path)
        except OSError as err:
            logger.exception('Cleanup error: %s', err)

    def __exit__(self, exc_type, exc_value, traceback):
        temp_path = Path(self.temp_path)
        assert_is_dir(temp_path)

        super().__exit__(exc_type, exc_value, traceback)

        assert not temp_path.is_dir(), f'ERROR: {temp_path!r} still exists?!?'

    def decorate_class(self, cls):
        raise NotImplementedError('Decorating a class is not supported!')

    def decorate_callable(self, func):
        self.prefix_candidate = f'{func.__name__}_'
        print(f"prefix from func {func!r}: {self.prefix_candidate!r}")
        return super().decorate_callable(func)
