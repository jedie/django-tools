"""
    :copyleft: 2017-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from django.test import SimpleTestCase

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.utils.installed_apps_utils import get_filtered_apps


class TestGetFilteredApps(SimpleTestCase):
    def test_get_filtered_apps1(self):
        apps = get_filtered_apps()
        assert_pformat_equal(apps, [])

    def test_get_filtered_apps2(self):
        apps = get_filtered_apps(no_args=False)
        assert_pformat_equal(apps, ["django.contrib.flatpages"])

    def test_get_filtered_apps3(self):
        apps = get_filtered_apps(
            resolve_url="login/",
            # debug=True
        )
        assert_pformat_equal(apps, ["django.contrib.auth"])

    def test_get_filtered_apps4(self):
        apps = get_filtered_apps(resolve_url="login/", no_args=False)
        assert_pformat_equal(apps, ["django.contrib.auth", "django.contrib.flatpages"])
