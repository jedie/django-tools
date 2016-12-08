# coding: utf-8

"""
    :copyleft: 2016 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.test import SimpleTestCase
from django.core.mail.backends.locmem import EmailBackend
from django.utils import six

from django_tools.cache.site_cache_middleware import UpdateCacheMiddleware
from django_tools.utils.importlib import ImproperlyConfigured, get_attr_from_string, get_setting, \
    get_attr_from_settings, get_class_instance_from_settings

if six.PY3:
    from unittest import mock
else:
    import mock # https://pypi.python.org/pypi/mock


class TestImportlib(SimpleTestCase):
    def test_get_attr_from_string(self):
        UpdateCacheMiddleware2 = get_attr_from_string("django_tools.cache.site_cache_middleware.UpdateCacheMiddleware")
        self.assertEqual(UpdateCacheMiddleware2, UpdateCacheMiddleware)

        with self.assertRaises(ImproperlyConfigured) as cm:
            get_attr_from_string("no point", "TEST")
        self.assertEqual(cm.exception.args[0], "no point isn't a TEST module")

        with self.assertRaises(ImproperlyConfigured) as cm:
            get_attr_from_string("django.core.doesntexists", "Foo Bar")
        self.assertEqual(cm.exception.args[0], 'Foo Bar module "django.core" does not define a "doesntexists" class')

        with self.assertRaises(ImproperlyConfigured) as cm:
            get_attr_from_string("django_tools.utils.importlib.not_exists", "Import Lib")
        self.assertEqual(cm.exception.args[0], 'Import Lib module "django_tools.utils.importlib" does not define a "not_exists" class')

    def test_get_setting(self):
        self.assertEqual(
            get_setting("EMAIL_BACKEND"),
            'django.core.mail.backends.locmem.EmailBackend'
        )

    @mock.patch('django_tools.utils.importlib.logger')
    def test_get_setting_not_exists(self, mock_logger):
        get_setting("DOESN'T EXISTS")
        mock_logger.debug.assert_called_with(
            '''"DOESN'T EXISTS" not in settings defined'''
        )

    @mock.patch('django_tools.utils.importlib.logger')
    def test_get_setting_empty(self, mock_logger):
        self.assertEqual(settings.STATIC_URL, None)
        get_setting("STATIC_URL")
        mock_logger.debug.assert_called_with(
            'settings.STATIC_URL is None or empty'
        )

    def test_get_attr_from_settings(self):
        obj = get_attr_from_settings("EMAIL_BACKEND", "email backend")
        self.assertIs(obj, EmailBackend)

    @mock.patch('django_tools.utils.importlib.logger')
    def test_get_attr_from_settings_not_exists(self, mock_logger):
        get_attr_from_settings("DOESN'T EXISTS", "a test")
        mock_logger.debug.assert_called_with(
            '''"DOESN'T EXISTS" not in settings defined'''
        )

    @mock.patch('django_tools.utils.importlib.logger')
    def test_get_attr_from_settings_empty(self, mock_logger):
        self.assertEqual(settings.STATIC_URL, None)
        get_attr_from_settings("STATIC_URL", "a test")
        mock_logger.debug.assert_called_with(
            'settings.STATIC_URL is None or empty'
        )

    def test_get_class_instance_from_settings(self):
        obj = get_class_instance_from_settings("EMAIL_BACKEND", "email backend")
        self.assertIsInstance(obj, EmailBackend)

    @mock.patch('django_tools.utils.importlib.logger')
    def test_get_class_instance_from_settings_not_exists(self, mock_logger):
        get_class_instance_from_settings("DOESN'T EXISTS", "a test")
        mock_logger.debug.assert_called_with(
            '''"DOESN'T EXISTS" not in settings defined'''
        )

    @mock.patch('django_tools.utils.importlib.logger')
    def test_get_class_instance_from_settings_empty(self, mock_logger):
        self.assertEqual(settings.STATIC_URL, None)
        get_class_instance_from_settings("STATIC_URL", "a test")
        mock_logger.debug.assert_called_with(
            'settings.STATIC_URL is None or empty'
        )

