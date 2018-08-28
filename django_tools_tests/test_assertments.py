"""
    :created: 28.08.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest

from django.test import SimpleTestCase

from celery import Celery

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import (
    assert_celery_always_eager, assert_endswith, assert_locmem_mail_backend, assert_startswith
)


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


class TestCeleryAssertments(SimpleTestCase):

    def test_default(self):
        assert_celery_always_eager()

    def test_app_kwarg(self):
        app = Celery("test_app_kwarg")
        app.conf.task_always_eager = True
        app.conf.task_eager_propagates = True
        assert_celery_always_eager(celery_app=app)

    def test_not_always_eager(self):
        app = Celery("test_not_always_eager")
        app.conf.task_always_eager = False
        app.conf.task_eager_propagates = True

        with self.assertRaises(AssertionError) as cm:
            assert_celery_always_eager(celery_app=app)

        assert_startswith(cm.exception.args[0], "<Celery test_not_always_eager at 0x")
        assert_endswith(cm.exception.args[0], "> not eager: False")

    def test_not_eager_propagates(self):
        app = Celery("test_not_eager_propagates")
        app.conf.task_always_eager = True
        app.conf.task_eager_propagates = False

        with self.assertRaises(AssertionError) as cm:
            assert_celery_always_eager(celery_app=app)

        assert_startswith(cm.exception.args[0], "<Celery test_not_eager_propagates at 0x")
        assert_endswith(cm.exception.args[0], "> not propagates: False")


class TestMailAssertments(SimpleTestCase):

    def test_assert_locmem_mail_backend(self):
        assert_locmem_mail_backend()
