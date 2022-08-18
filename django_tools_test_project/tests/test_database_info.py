"""
    Test /django_tools/management/commands/database_info.py

    :copyleft: 2017-2022 by the django-tools team, see AUTHORS for more details.
    :created: 2017 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from pathlib import Path
from unittest import TestCase

from django.test import SimpleTestCase

import django_tools_test_project
from django_tools.management.commands import database_info
from django_tools.unittest_utils.call_management_commands import captured_call_command
from django_tools.unittest_utils.django_command import DjangoCommandMixin


MANAGE_DIR = Path(django_tools_test_project.__file__).parent


class DatabaseInfoCallCommandTests(SimpleTestCase):
    """
    Test directly via django.core.management.call_command()
    Note:
        So the test database settings is active.
    """

    def test_database_info(self):
        output, stderr = captured_call_command(command=database_info)
        assert stderr == ''

        self.assertIn("engine...............: 'sqlite3'", output)

        self.assertTrue(
            "name.................: ':memory:'" in output
            or
            "name.................: 'file:memorydb_default?mode=memory&cache=shared'" in output
        )

        self.assertIn("There are 1 connections.", output)

        self.assertIn("'CONN_MAX_AGE': 0,", output)


class DatabaseInfoSubprocessTests(DjangoCommandMixin, TestCase):
    """
    Test command via "manage.py" subprocess
    Note:
        So the real database settings is active and not the test settings!
    """

    def test_database_info(self):
        output = self.call_manage_py(["database_info"], manage_dir=MANAGE_DIR)
        print(output)
        self.assertIn("engine...............: 'sqlite3'", output)
        self.assertIn("name.................:", output)
        self.assertIn("test_project_db.sqlite3", output)

        self.assertIn("There are 1 connections.", output)

        self.assertIn("'CONN_MAX_AGE': 0,", output)
