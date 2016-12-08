# coding: utf-8

"""
    Test django_tools.unittest_utils.django_command
"""

from __future__ import unicode_literals, print_function


import os
from django.conf import settings

from unittest import TestCase

import django_tools
from django_tools.unittest_utils.django_command import DjangoCommandMixin


MANAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(django_tools.__file__), ".."))

class TestListModelsCommand(DjangoCommandMixin, TestCase):
    def test_help(self):
        output = self.call_manage_py(["--help"], manage_dir=MANAGE_DIR)

        self.assertNotIn("ERROR", output)
        self.assertIn("[django]", output)
        self.assertIn("[django_tools_list_models]", output)
        self.assertIn("list_models", output)

    def test_list_models(self):
        output = self.call_manage_py(["list_models"], manage_dir=MANAGE_DIR)
        print(output)

        self.assertNotIn("ERROR", output)
        self.assertIn("existing models in app_label.ModelName format:", output)

        self.assertIn("01 - admin.LogEntry", output)
        self.assertIn("02 - auth.Group", output)

        self.assertIn("06 - django_tools_test_app.LimitToUsergroupsTestModel", output)
        self.assertIn("07 - dynamic_site.SiteAlias", output)

        # TODO: Add numbers after django-filer v1.2.6 is released!
        # see:
        # https://github.com/jedie/django-tools/commit/b427e148c2decd3410239152550bf509854b78be
        self.assertIn("INSTALLED_APPS....:", output)
        self.assertIn("Apps with models..:", output)

class TestNiceDiffSettingsCommand(DjangoCommandMixin, TestCase):
    def test_help(self):
        output = self.call_manage_py(["--help"], manage_dir=MANAGE_DIR)

        self.assertNotIn("ERROR", output)
        self.assertIn("[django]", output)
        self.assertIn("[django_tools_nice_diffsettings]", output)
        self.assertIn("nice_diffsettings", output)

    def test_nice_diffsettings(self):
        output = self.call_manage_py(["nice_diffsettings"], manage_dir=MANAGE_DIR)
        print(output)

        self.assertNotIn("ERROR", output)
        self.assertIn("\n\nSETTINGS_MODULE = 'django_tools_test_project.test_settings'\n\n", output)
        self.assertIn("\n\nINSTALLED_APPS = ('django.contrib.auth',\n", output)
