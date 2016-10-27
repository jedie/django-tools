# coding: utf-8

"""
    Test django_tools.unittest_utils.django_command
"""

from __future__ import unicode_literals, print_function


import os

from unittest import TestCase

import django_tools
from django_tools.unittest_utils.django_command import DjangoCommandMixin


class TestDjangoCommand(DjangoCommandMixin, TestCase):
    def test_help(self):
        manage_dir = os.path.abspath(os.path.join(os.path.dirname(django_tools.__file__), ".."))
        output = self.call_manage_py(["--help"], manage_dir)

        self.assertNotIn("ERROR", output)
        self.assertIn("[django]", output)
        self.assertIn("Type 'manage.py help <subcommand>' for help on a specific subcommand.", output)