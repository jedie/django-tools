from functools import wraps
import unittest

from django.test import SimpleTestCase


class _Mock(object):
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, test_func):
        @wraps(test_func)
        def inner(*args, **kwargs):
            return test_func(*args, **kwargs)
        return inner

try:
    from django.test.utils import modify_settings
except ImportError:
    # modify_settings is new in Django 1.7
    modify_settings = _Mock

from django_tools.utils.installed_apps_utils import get_filtered_apps


@unittest.skipIf(isinstance(modify_settings, _Mock), "SKIP: modify_settings is not available :(")
@modify_settings(INSTALLED_APPS={
    'prepend': [
        'django.contrib.admindocs',
        'django.contrib.flatpages',
    ]
})
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
        self.assertEqual(apps, ['django.contrib.flatpages', 'django.contrib.auth'])

