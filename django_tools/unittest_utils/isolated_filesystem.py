import os
import shutil
import tempfile
from pathlib import Path

from django.test.utils import TestContextDecorator


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

    or:

    @isolated_filesystem()
    class FooBarTestCase(TestCase):
        def test_foo(self):
            print("I'm in the temp path here: %s" % Path().cwd())
    """
    def __init__(self, prefix=None):
        super().__init__()

        self.prefix = prefix
        self.prefix_candidate = None

    def enable(self):
        if self.prefix is None:
            prefix = self.prefix_candidate
        else:
            prefix = self.prefix

        print("Use prefix: %r" % prefix)

        self.cwd = Path().cwd()
        self.temp_path = tempfile.mkdtemp(prefix=prefix)
        os.chdir(self.temp_path)

    def disable(self):
        os.chdir(str(self.cwd)) # str() needed for older python <=3.5
        try:
            shutil.rmtree(self.temp_path)
        except (OSError, IOError):
            pass

    def decorate_class(self, cls):
        self.prefix_candidate = cls.__name__
        print("prefix from class %r: %r" % (cls, self.prefix_candidate))
        return super().decorate_class(cls)

    def decorate_callable(self, func):
        self.prefix_candidate = func.__name__
        print("prefix from func %r: %r" % (func, self.prefix_candidate))
        return super().decorate_callable(func)
