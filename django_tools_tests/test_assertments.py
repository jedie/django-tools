"""
    :created: 28.08.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest

from django.test import SimpleTestCase

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_endswith, assert_locmem_mail_backend, assert_startswith


class TestStringAssertments(unittest.TestCase):

    def test_startswith(self):
        assert_startswith("foobar", "foo")

    def test_not_startswith(self):

        with self.assertRaises(AssertionError) as cm:
            assert_startswith("foo", "bar")

        self.assertEqual(cm.exception.args[0], "'foo' doesn't starts with 'bar'")

    def test_endswith(self):
        assert_endswith("foobar", "bar")

    def test_not_endswith(self):

        with self.assertRaises(AssertionError) as cm:
            assert_endswith("foo", "bar")

        self.assertEqual(cm.exception.args[0], "'foo' doesn't ends with 'bar'")


class TestMailAssertments(SimpleTestCase):

    def test_assert_locmem_mail_backend(self):
        assert_locmem_mail_backend()
