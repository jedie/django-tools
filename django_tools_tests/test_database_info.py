# coding: utf-8

"""
    Test /django_tools/management/commands/database_info.py

    :copyleft: 2017 by the django-tools team, see AUTHORS for more details.
    :created: 2017 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import print_function, unicode_literals

import os
import sys
from unittest import TestCase

import django
from django.core.management import call_command
from django.test import SimpleTestCase

# https://github.com/jedie/django-tools
import django_tools
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer

MANAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(django_tools.__file__), ".."))


class DatabaseInfoCallCommandTests(SimpleTestCase):
    """
    Test directly via django.core.management.call_command()
    Note:
        So the test database settings is active.
    """
    def test_database_info(self):
        with StdoutStderrBuffer() as buff:
            call_command("database_info")
        output = buff.get_output()
        print(output)

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
        self.assertIn("name.................: ':memory:'", output)

        self.assertIn("There are 1 connections.", output)

        self.assertIn("'CONN_MAX_AGE': 0,", output)
