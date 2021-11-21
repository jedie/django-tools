"""
    Test django_tools.unittest_utils.django_command

    :copyleft: 2017-2021 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from pathlib import Path

from bx_py_utils.test_utils.snapshot import assert_text_snapshot
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase

import django_tools
import django_tools_test_project
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.user import TestUserMixin


REPO_PATH = str(Path(django_tools.__file__).parent.parent.parent)
MANAGE_DIR = Path(django_tools_test_project.__file__).parent


class CommandTestCase(TestUserMixin, DjangoCommandMixin, TestCase):
    def test_help(self):
        output = self.call_manage_py(["--help"], manage_dir=MANAGE_DIR)

        self.assertIn("[django]", output)
        self.assertIn("[django_tools]", output)
        self.assertIn("nice_diffsettings", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

        assert 'Use settings: ' in output
        assert REPO_PATH in output
        output = output.replace(REPO_PATH, '...')
        assert_text_snapshot(got=output)

    def test_list_models(self):
        output = self.call_manage_py(
            ["list_models"], manage_dir=MANAGE_DIR,  # debug=True
        )
        assert "existing models in app_label.ModelName format:" in output
        output = output.split("existing models in app_label.ModelName format:", 1)[1]

        assert '01 - admin.LogEntry' in output
        assert 'INSTALLED_APPS....:' in output
        assert 'Apps with models..:' in output

        assert REPO_PATH not in output
        assert_text_snapshot(got=output)

    def test_nice_diffsettings(self):
        output = self.call_manage_py(["nice_diffsettings"], manage_dir=MANAGE_DIR)

        self.assertIn("\n\nSETTINGS_MODULE = 'django_tools_test_project.settings.test'\n\n", output)
        self.assertIn("\n\nINSTALLED_APPS = ('django.contrib.auth',\n", output)

        self.assertNotIn("Traceback ", output)  # Space after Traceback is important ;)
        self.assertNotIn("ERROR", output)

        assert 'Use settings: ' in output
        assert REPO_PATH in output
        output = output.replace(REPO_PATH, '...')
        assert_text_snapshot(got=output)

    def test_environment(self):
        usernames = ",".join(self.UserModel.objects.values_list("username", flat=True).order_by("username"))
        assert_pformat_equal(usernames, "normal_test_user,staff_test_user,superuser")

    def test_no_username_given(self):
        with StdoutStderrBuffer() as buff:
            call_command("permission_info")
        output = buff.get_output()

        self.assertIn("All existing users are:", output)
        self.assertIn("normal_test_user, staff_test_user, superuser", output)
        self.assertIn("(3 users)", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

        assert REPO_PATH not in output
        assert_text_snapshot(got=output)

    def test_wrong_username_given(self):
        with StdoutStderrBuffer() as buff:
            call_command("permission_info", "not existing username")
        output = buff.get_output()

        self.assertIn("Username 'not existing username' doesn't exists", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

        assert REPO_PATH not in output
        assert_text_snapshot(got=output)

    def test_normal_test_user(self):
        with StdoutStderrBuffer() as buff:
            call_command("permission_info", "normal_test_user")
        output = buff.get_output()

        self.assertIn("Display effective user permissions", output)
        self.assertIn("is_active    : yes", output)
        self.assertIn("is_staff     : no", output)
        self.assertIn("is_superuser : no", output)

        self.assertIn("[ ] auth.add_user", output)
        self.assertIn("[ ] sites.delete_site", output)

        self.assertNotIn("[*]", output)  # normal user hasn't any permissions ;)
        self.assertNotIn("missing:", output)  # no missing permissions

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

        assert REPO_PATH not in output
        assert_text_snapshot(got=output)

    def test_update_permissions(self):
        with StdoutStderrBuffer() as buff:
            call_command("update_permissions")
        output = buff.get_output()

        self.assertIn("Create permissions for:", output)
        self.assertIn(" * auth", output)
        self.assertIn(" * django_tools_test_app", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

        assert REPO_PATH not in output
        assert_text_snapshot(got=output)

    def test_clear_cache(self):

        cache.set("key_foo", "bar", 30)
        assert_pformat_equal(cache.get("key_foo"), "bar")

        with StdoutStderrBuffer() as buff:
            call_command("clear_cache")
        output = buff.get_output()

        assert_pformat_equal(cache.get("key_foo"), None)

        self.assertIn("Clear caches:", output)
        self.assertIn("Clear 'LocMemCache'", output)
        self.assertIn("done.", output)

        self.assertNotIn("Traceback", output)
        self.assertNotIn("ERROR", output)

        assert REPO_PATH not in output
        assert_text_snapshot(got=output)
