"""
    :created: 11.12.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import unittest

# https://github.com/jedie/django-tools
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
