"""
    :copyleft: 2017-2020 by the django-tools team, see AUTHORS for more details.
    :created: 2017 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from pathlib import Path
from unittest import TestCase

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase

# https://github.com/jedie/django-tools
import django_tools_test_project
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer


MANAGE_DIR = Path(django_tools_test_project.__file__).parent


class SettingsTests(SimpleTestCase):

    def test_settings_module(self):
        self.assertIn('django_tools_test_project.settings.test', settings.SETTINGS_MODULE)

    def test_diffsettings(self):
        """
        Check some settings
        """
        with StdoutStderrBuffer() as buff:
            call_command('diffsettings')
        output = buff.get_output()
        print(output)
        self.assertIn('django_tools_test_project.settings.test', output)  # SETTINGS_MODULE


class ManageCommandTests(DjangoCommandMixin, TestCase):

    def test_help(self):
        """
        Run './manage.py --help' via subprocess and check output.
        """
        output = self.call_manage_py(['--help'], manage_dir=MANAGE_DIR)

        self.assertNotIn('ERROR', output)
        self.assertIn('[django]', output)
        self.assertIn('Type \'manage.py help <subcommand>\' for help on a specific subcommand.', output)


class ManageCheckTests(SimpleTestCase):

    def test_django_check(self):
        """
        call './manage.py check' directly via 'call_command'
        """
        with StdoutStderrBuffer() as buff:
            call_command('check')
        output = buff.get_output()
        self.assertIn('System check identified no issues (0 silenced).', output)
