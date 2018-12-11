import unittest

from django_tools.decorators import warn_class_usage, warn_function_usage


class TestWarnDecorators(unittest.TestCase):
    def test_warn_class_usage(self):

        @warn_class_usage(message="Test warn class usage !")
        class FooBar:
            pass

        with self.assertWarns(DeprecationWarning) as cm:
            FooBar()

        self.assertEqual(str(cm.warning), "Test warn class usage !")

    def test_warn_function_usage(self):

        @warn_function_usage(message="Test warn function usage !")
        def foo_bar():
            pass

        with self.assertWarns(DeprecationWarning) as cm:
            foo_bar()

        self.assertEqual(str(cm.warning), "Test warn function usage !")
