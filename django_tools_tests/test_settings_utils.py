
"""
    :created: 2017 by Jens Diemer
    :copyleft: 2017 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest

from django.http.request import validate_host

# https://github.com/jedie/django-tools
from django_tools.settings_utils import FnMatchIps


class TestSettingsUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fnmatch_ips = FnMatchIps(["127.0.0.1", "::1", "192.168.*.*"])

    def test_contains(self):
        # INTERNAL_IPS used this
        self.assertTrue(
            "192.168.1.2" in self.fnmatch_ips
        )
        self.assertFalse(
            "10.0.1.2" in self.fnmatch_ips
        )

    def test_compare(self):
        # ALLOWED_HOSTS with django.http.request.validate_host

        self.assertTrue(
            validate_host("192.168.1.2", self.fnmatch_ips)
        )

        self.assertFalse(
            validate_host("10.0.1.2", self.fnmatch_ips)
        )
