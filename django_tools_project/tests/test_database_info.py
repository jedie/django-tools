"""
    Test /django_tools/management/commands/database_info.py

    :copyleft: 2017-2022 by the django-tools team, see AUTHORS for more details.
    :created: 2017 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from unittest import TestCase

from cli_base.cli_tools.test_utils.assertion import assert_in
from django.test import SimpleTestCase

from django_tools.management.commands import database_info
from django_tools.unittest_utils.call_management_commands import captured_call_command
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools_project.constants import PACKAGE_ROOT


class DatabaseInfoCallCommandTests(SimpleTestCase):
    """
    Test directly via django.core.management.call_command()
    Note:
        So the test database settings is active.
    """

    def test_database_info(self):
        output, stderr = captured_call_command(command=database_info)
        assert stderr == ''
        assert_in(
            content=output,
            parts=(
                "engine...............: 'sqlite3'",
                "There are 1 connections.",
                "'CONN_MAX_AGE': 0,",
            ),
        )
        self.assertTrue(
            "name.................: ':memory:'" in output
            or "name.................: 'file:memorydb_default?mode=memory&cache=shared'" in output
        )


class DatabaseInfoSubprocessTests(DjangoCommandMixin, TestCase):
    """
    Test command via "manage.py" subprocess
    Note:
        So the real database settings is active and not the test settings!
    """

    def test_database_info(self):
        output = self.call_manage_py(["database_info"], manage_dir=PACKAGE_ROOT)
        assert_in(
            content=output,
            parts=(
                "engine...............: 'sqlite3'",
                "name.................: ':memory:'",
                "There are 1 connections.",
                "'CONN_MAX_AGE': 0,",
            ),
        )
