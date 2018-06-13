
from django.test import SimpleTestCase

# https://github.com/jedie/django-tools
from django_tools.utils.installed_apps_utils import get_filtered_apps


class TestGetFilteredApps(SimpleTestCase):
    def test_get_filtered_apps1(self):
        apps = get_filtered_apps()
        self.assertEqual(apps, [])

    def test_get_filtered_apps2(self):
        apps = get_filtered_apps(no_args=False)
        self.assertEqual(apps, ['django.contrib.flatpages'])

    def test_get_filtered_apps3(self):
        apps = get_filtered_apps(resolve_url="login/",
            # debug=True
        )
        self.assertEqual(apps, ['django.contrib.auth'])

    def test_get_filtered_apps4(self):
        apps = get_filtered_apps(resolve_url="login/", no_args=False)
        self.assertEqual(apps, ['django.contrib.auth', 'django.contrib.flatpages'])
