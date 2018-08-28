# coding: utf-8

"""
    :copyleft: 2017 by the django-tools team, see AUTHORS for more details.
    :created: 2017 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import print_function, unicode_literals

import os
from unittest import TestCase

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

# https://github.com/jedie/django-tools
import django_tools
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer

MANAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(django_tools.__file__), ".."))


class SettingsTests(SimpleTestCase):

    def test_settings_module(self):
        self.assertIn('django_tools_test_project.test_settings', settings.SETTINGS_MODULE)

    def test_diffsettings(self):
        """
        Check some settings
        """
        with StdoutStderrBuffer() as buff:
            call_command('diffsettings')
        output = buff.get_output()
        print(output)
        self.assertIn('django_tools_test_project.test_settings', output) # SETTINGS_MODULE

        self.assertIn('CELERY_TASK_ALWAYS_EAGER = True', output)
        self.assertIn('CELERY_TASK_EAGER_PROPAGATES = True', output)


class ManageCommandTests(DjangoCommandMixin, TestCase):

    def test_help(self):
        """
        Run './manage.py --help' via subprocess and check output.
        """
        output = self.call_manage_py(['--help'], manage_dir=MANAGE_DIR)

        self.assertNotIn('ERROR', output)
        self.assertIn('[django]', output)
        self.assertIn('Type \'manage.py help <subcommand>\' for help on a specific subcommand.', output)

    # def test_unapplied_migrations(self):
    #     output = self.call_manage_py(["showmigrations"], manage_dir=MANAGE_DIR)
    #     print(output)
    #
    #     # We didn't have any migrations, yet:
    #     # self.assertIn('[X]', output) # applied migration
    #
    #     self.assertNotIn("[ ]", output) # unapplied migration

    def test_missing_migrations(self):
        output = self.call_manage_py(["makemigrations", "--dry-run"], manage_dir=MANAGE_DIR)
        print(output)
        self.assertIn("No changes detected", output)
        self.assertNotIn("Migrations for", output) # output like: """Migrations for 'appname':"""
        self.assertNotIn("SystemCheckError", output)
        self.assertNotIn("ERRORS", output)


class ManageCheckTests(SimpleTestCase):

    def test_django_check(self):
        """
        call './manage.py check' directly via 'call_command'
        """
        with StdoutStderrBuffer() as buff:
            call_command('check')
        output = buff.get_output()
        self.assertIn('System check identified no issues (0 silenced).', output)
