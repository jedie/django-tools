# coding: utf-8

"""
    Test django_tools.unittest_utils.django_command
"""

from __future__ import print_function, unicode_literals

import os

import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase

# https://github.com/jedie/django-tools
import django_tools
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.user import TestUserMixin

MANAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(django_tools.__file__), ".."))


class TestListModelsCommand(DjangoCommandMixin, TestCase):
    def test_help(self):
        output = self.call_manage_py(["--help"], manage_dir=MANAGE_DIR)

        self.assertIn("[django]", output)
        self.assertIn("[django_tools_list_models]", output)
        self.assertIn("list_models", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

    def test_list_models(self):
        output = self.call_manage_py(["list_models"], manage_dir=MANAGE_DIR)
        print(output)

        self.assertIn("existing models in app_label.ModelName format:", output)

        self.assertIn("01 - admin.LogEntry", output)
        self.assertIn("02 - auth.Group", output)

        self.assertIn("06 - django_tools_test_app.LimitToUsergroupsTestModel", output)
        self.assertIn("07 - django_tools_test_app.PermissionTestModel", output)

        self.assertIn("INSTALLED_APPS....: 15", output)
        self.assertIn("Apps with models..: 15", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

class TestNiceDiffSettingsCommand(DjangoCommandMixin, TestCase):
    def test_help(self):
        output = self.call_manage_py(["--help"], manage_dir=MANAGE_DIR)

        self.assertIn("[django]", output)
        self.assertIn("[django_tools_nice_diffsettings]", output)
        self.assertIn("nice_diffsettings", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

    def test_nice_diffsettings(self):
        output = self.call_manage_py(["nice_diffsettings"], manage_dir=MANAGE_DIR)
        print(output)

        self.assertIn("\n\nSETTINGS_MODULE = 'django_tools_test_project.test_settings'\n\n", output)
        self.assertIn("\n\nINSTALLED_APPS = ('django.contrib.auth',\n", output)

        self.assertNotIn("Traceback ", output) # Space after Traceback is important ;)
        self.assertNotIn("ERROR", output)


@pytest.mark.django_db
class TestPermissionInfoCommand(TestUserMixin, DjangoCommandMixin, TestCase):
    def test_environment(self):
        usernames = ",".join(
            self.UserModel.objects.values_list("username", flat=True).order_by("username")
        )
        self.assertEqual(usernames, "normal_test_user,staff_test_user,superuser")

    def test_help(self):
        output = self.call_manage_py(["--help"], manage_dir=MANAGE_DIR)

        self.assertIn("[django]", output)
        self.assertIn("permission_info", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

    def test_no_username_given(self):
        with StdoutStderrBuffer() as buff:
            call_command("permission_info")
        output = buff.get_output()
        print(output)

        self.assertIn("All existing users are:", output)
        self.assertIn("normal_test_user, staff_test_user, superuser", output)
        self.assertIn("(3 users)", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

    def test_wrong_username_given(self):
        with StdoutStderrBuffer() as buff:
            call_command("permission_info", "not existing username")
        output = buff.get_output()
        print(output)

        self.assertIn("Username 'not existing username' doesn't exists", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

    def test_normal_test_user(self):
        with StdoutStderrBuffer() as buff:
            call_command("permission_info", "normal_test_user")
        output = buff.get_output()
        print(output)

        self.assertIn("Display effective user permissions", output)
        self.assertIn("is_active    : yes", output)
        self.assertIn("is_staff     : no", output)
        self.assertIn("is_superuser : no", output)

        self.assertIn("[ ] auth.add_user", output)
        self.assertIn("[ ] sites.delete_site", output)

        self.assertNotIn("[*]", output) # normal user hasn't any permissions ;)
        self.assertNotIn("missing:", output) # no missing permissions

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)


class TestUpdatePermissionCommand(TestUserMixin, DjangoCommandMixin, TestCase):
    """
    Test for:
    django_tools.management.commands.update_permissions.Command
    """
    def test_help(self):
        output = self.call_manage_py(["--help"], manage_dir=MANAGE_DIR)

        self.assertIn("[django]", output)
        self.assertIn("update_permissions", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

    def test_update_permissions(self):
        with StdoutStderrBuffer() as buff:
            call_command("update_permissions")
        output = buff.get_output()
        print(output)

        self.assertIn("Create permissions for:", output)
        self.assertIn(" * auth", output)
        self.assertIn(" * django_tools_test_app", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)


class TestClearCacheCommand(DjangoCommandMixin, TestCase):
    """
    Test for:
    django_tools.management.commands.clear_cache.Command
    """
    def test_help(self):
        output = self.call_manage_py(["--help"], manage_dir=MANAGE_DIR)

        self.assertIn("[django]", output)
        self.assertIn("clear_cache", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

    def test_clear_cache(self):

        cache.set("key_foo", "bar", 30)
        self.assertEqual(cache.get("key_foo"), "bar")

        with StdoutStderrBuffer() as buff:
            call_command("clear_cache")
        output = buff.get_output()
        print(output)

        self.assertEqual(cache.get("key_foo"), None)

        self.assertIn("Clear caches:", output)
        self.assertIn("Clear 'LocMemCache'", output)
        self.assertIn("done.", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)


