"""
    Test django_tools.unittest_utils.django_command
"""

import os
from pathlib import Path
from unittest import TestCase

# https://github.com/jedie/django-tools
import django_tools_test_project
from django_tools.unittest_utils.django_command import DjangoCommandMixin


MANAGE_DIR = Path(django_tools_test_project.__file__).parent


class TestDjangoCommand(DjangoCommandMixin, TestCase):
    def test_help(self):
        output = self.call_manage_py(["--help"], manage_dir=MANAGE_DIR)

        self.assertNotIn("ERROR", output)
        self.assertIn("[django]", output)
        self.assertIn(
            "Type 'manage.py help <subcommand>' for help on a specific subcommand.", output
        )

    def test_check(self):
        output = self.call_manage_py(["check"], manage_dir=MANAGE_DIR)
        self.assertNotIn("ERROR", output)
        self.assertIn("System check identified no issues (0 silenced).", output)

    def test_set_env(self):
        """
        Test if we can set "DJANGO_SETTINGS_MODULE"
        """
        env = dict(os.environ)
        env["DJANGO_SETTINGS_MODULE"] = "does-not-exist"

        with self.assertRaises(AssertionError) as cm:
            self.call_manage_py(
                ["diffsettings"], manage_dir=MANAGE_DIR, env=env,  # debug=True
            )

        output = "\n".join(cm.exception.args)
        print(output)

        self.assertIn("subprocess exist status == 1", output)

    def test_excepted_exit_code(self):
        output = self.call_manage_py(
            ["NotExistingCommand"], excepted_exit_code=1, manage_dir=MANAGE_DIR
        )
        print(output)
        self.assertIn("Unknown command: 'NotExistingCommand'", output)
