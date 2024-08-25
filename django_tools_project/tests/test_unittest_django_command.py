"""
    Test django_tools.unittest_utils.django_command
"""

import os
from unittest import mock

from bx_django_utils.test_utils.html_assertion import get_django_name_suffix
from bx_py_utils.test_utils.snapshot import assert_text_snapshot
from cli_base.cli_tools.test_utils.assertion import assert_in
from django.core.cache import cache
from django.core.management import BaseCommand, call_command
from django.test import TestCase

import django_tools
from django_tools.management.commands import list_models, run_testserver
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.unittest_utils.call_management_commands import captured_call_command
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.user import TestUserMixin
from django_tools_project.constants import PACKAGE_ROOT


REPO_PATH = str(PACKAGE_ROOT)


class TestDjangoCommand(TestUserMixin, DjangoCommandMixin, TestCase):

    def clean_manage_output(self, output: str) -> str:
        lines = output.splitlines()
        for index, line in enumerate(lines):
            if django_tools.__version__ in line:
                lines[index] = '[replaced django_tools.__version__]'
                output = '\n'.join(lines)
                break

        output = output.replace(REPO_PATH, '.../django-tools')
        output = output.strip()
        return output

    def test_help(self):
        """
        Run './manage.py --help' via subprocess and check output.
        """
        output = self.call_manage_py(['--help'], manage_dir=PACKAGE_ROOT)

        self.assertNotIn('ERROR', output)
        self.assertNotIn('Traceback', output)
        assert_in(
            content=output,
            parts=(
                'django_tools_project',
                'Available subcommands:',
                '[django]',
                '[django_tools]',
                '[manage_django_project]',
                '\nDJANGO_SETTINGS_MODULE=django_tools_project.settings.tests\n',
            ),
        )
        assert_text_snapshot(got=self.clean_manage_output(output), name_suffix=get_django_name_suffix())

    def test_list_models(self):
        output, stderr = captured_call_command(command=list_models)
        assert stderr == ''
        assert_in(
            content=output,
            parts=(
                'existing models in app_label.ModelName format:',
                '01 - admin.LogEntry',
                'INSTALLED_APPS....:',
                'Apps with models..:',
            ),
        )
        self.assertNotIn(REPO_PATH, output)
        assert_text_snapshot(got=output)

    def test_set_env(self):
        """
        Test if we can set "DJANGO_SETTINGS_MODULE"
        """
        env = os.environ.copy()
        env["DJANGO_SETTINGS_MODULE"] = "does-not-exist"

        with self.assertRaises(AssertionError) as cm:
            self.call_manage_py(
                ["diffsettings"],
                manage_dir=PACKAGE_ROOT,
                env=env,  # debug=True
            )

        output = "\n".join(cm.exception.args)
        self.assertIn("subprocess exist status == 1", output)

    def test_excepted_exit_code(self):
        output = self.call_manage_py(["NotExistingCommand"], excepted_exit_code=1, manage_dir=PACKAGE_ROOT)
        self.assertIn("Unknown command: 'NotExistingCommand'", output)

    def test_nice_diffsettings(self):
        output = self.call_manage_py(["nice_diffsettings"], excepted_exit_code=0, manage_dir=PACKAGE_ROOT)

        self.assertIn("\n\nSETTINGS_MODULE = 'django_tools_project.settings.tests'\n\n", output)
        self.assertIn("\n\nINSTALLED_APPS = [\n", output)

        self.assertNotIn("Traceback ", output)  # Space after Traceback is important ;)
        self.assertNotIn("ERROR", output)

        assert_text_snapshot(got=self.clean_manage_output(output), name_suffix=get_django_name_suffix())

    def test_environment(self):
        usernames = ','.join(self.UserModel.objects.values_list('username', flat=True).order_by('username'))
        assert_pformat_equal(usernames, 'normal_test_user,staff_test_user,superuser')

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

    def test_run_testserver_help(self):
        output = self.call_manage_py(['run_testserver', '--help'], excepted_exit_code=0, manage_dir=PACKAGE_ROOT)
        assert 'Setup test project and run django developer server' in output

        # From own run_testserver command:
        assert '--nomakemigrations' in output
        assert '--nomigrate' in output

        # From django.core.management.commands.runserver command:
        assert '[addrport]' in output

    def test_run_testserver_invalid_addr(self):
        output = self.call_manage_py(
            ['run_testserver', '--nomigrate', '--nomakemigrations', 'invalid:addr'],
            manage_dir=PACKAGE_ROOT,
            excepted_exit_code=1,
            # debug=True,
        )

        assert_in(
            output,
            parts=(
                'Call "runserver"',
                'is not a valid port number or address',
            ),
        )

    def test_run_testserver(self):
        class Mock:
            def __init__(self):
                self.call_info = []

            def __call__(self, command, **kwargs):
                assert isinstance(command, BaseCommand)
                for k, v in kwargs.items():
                    if hasattr(v, '__class__'):
                        kwargs[k] = v.__class__.__name__

                self.call_info.append({'command': command.__module__, 'kwargs': kwargs})

        call_command_mock = Mock()

        with mock.patch.object(run_testserver, 'call_command', call_command_mock):
            output, stderr = captured_call_command(command=run_testserver)
            assert stderr == ''

            assert_in(
                output,
                parts=(
                    'Call "makemigrations"',
                    'Call "migrate"',
                    'Call "runserver"',
                ),
            )

        call_info = call_command_mock.call_info
        self.assertEqual(
            call_info,
            [
                {
                    'command': 'django.core.management.commands.makemigrations',
                    'kwargs': {'stdout': 'OutputWrapper', 'stderr': 'OutputWrapper'},
                },
                {
                    'command': 'django.core.management.commands.migrate',
                    'kwargs': {'stdout': 'OutputWrapper', 'stderr': 'OutputWrapper'},
                },
                {
                    'command': 'django.contrib.staticfiles.management.commands.runserver',
                    'kwargs': {
                        'verbosity': 'int',
                        'settings': 'NoneType',
                        'pythonpath': 'NoneType',
                        'traceback': 'bool',
                        'no_color': 'bool',
                        'force_color': 'bool',
                        'addrport': 'NoneType',
                        'use_ipv6': 'bool',
                        'use_threading': 'bool',
                        'use_reloader': 'bool',
                        'skip_checks': 'bool',
                        'stdout': 'OutputWrapper',
                        'stderr': 'OutputWrapper',
                    },
                },
            ],
        )
        assert_text_snapshot(got=self.clean_manage_output(output))
