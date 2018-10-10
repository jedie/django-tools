"""
    :created: 28.08.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest
from pathlib import Path

from django.test import SimpleTestCase

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import (
    assert_endswith, assert_installed_apps, assert_is_dir, assert_is_file, assert_language_code,
    assert_locmem_mail_backend, assert_path_not_exists, assert_startswith
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


class TestMailAssertments(SimpleTestCase):
    def test_assert_locmem_mail_backend(self):
        assert_locmem_mail_backend()


class TestLanguageCodeAssertments(unittest.TestCase):
    def test_assert_language_code(self):
        assert_language_code(language_code="de")
        assert_language_code(language_code="en")

    def test_assert_language_code_failed(self):
        self.assertRaises(AssertionError, assert_language_code, language_code="XX")


class TestInstalledAppsAssertments(unittest.TestCase):
    def test_assert_installed_apps(self):
        assert_installed_apps(app_names=["django.contrib.sessions", "django.contrib.admin"])

    def test_assert_installed_apps_failed(self):
        self.assertRaises(AssertionError, assert_installed_apps, app_names=("foo", "bar"))


class TestPathAssertments(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.existing_file_path = Path(__file__)
        assert cls.existing_file_path.is_file()
        cls.existing_dir_path = cls.existing_file_path.parent
        assert cls.existing_dir_path.is_dir()

    def test_is_existing_dir_with_path_instance(self):
        assert_is_dir(self.existing_dir_path)

    def test_is_existing_dir_with_string(self):
        assert_is_dir(str(self.existing_dir_path))

    def test_is_dir_failed(self):
        with self.assertRaises(AssertionError) as cm:
            assert_is_dir("/does/not/exists/")

        self.assertEqual(cm.exception.args[0], "Directory not exists: /does/not/exists")

    def test_is_existing_file_with_path_instance(self):
        assert_is_file(self.existing_file_path)

    def test_is_existing_file_with_string(self):
        assert_is_file(str(self.existing_file_path))

    def test_is_file_failed_not_directory(self):
        with self.assertRaises(AssertionError) as cm:
            assert_is_file("/path/to/does/not/exists/foo.txt")

        self.assertEqual(cm.exception.args[0], "Directory not exists: /path/to/does/not/exists")

    def test_is_file_failed_file_not_exists(self):
        with self.assertRaises(AssertionError) as cm:
            assert_is_file("/notexisting.txt")

        self.assertEqual(cm.exception.args[0], "File not exists: /notexisting.txt")

    def test_assert_path_not_exists(self):
        assert_path_not_exists("/path/to/does/not/exists/foo.txt")

    def test_assert_path_not_exists_is_file(self):
        with self.assertRaises(AssertionError) as cm:
            assert_path_not_exists(self.existing_file_path)

        self.assertEqual(cm.exception.args[0], "Path is a existing file: %s" % self.existing_file_path)

    def test_assert_path_not_exists_is_dir(self):
        with self.assertRaises(AssertionError) as cm:
            assert_path_not_exists(str(self.existing_dir_path))

        self.assertEqual(cm.exception.args[0], "Path is a existing directory: %s" % self.existing_dir_path)
