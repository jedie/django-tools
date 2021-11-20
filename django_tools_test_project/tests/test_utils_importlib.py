"""
    :copyleft: 2016-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from unittest import mock

from django.conf import settings
from django.core.mail.backends.locmem import EmailBackend
from django.test import SimpleTestCase, override_settings

# https://github.com/jedie/django-tools
from django_tools.cache.site_cache_middleware import UpdateCacheMiddleware
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.utils.importlib import (
    ImproperlyConfigured,
    get_attr_from_settings,
    get_attr_from_string,
    get_class_instance_from_settings,
    get_setting,
)


class TestImportlib(SimpleTestCase):
    def test_get_attr_from_string(self):
        UpdateCacheMiddleware2 = get_attr_from_string("django_tools.cache.site_cache_middleware.UpdateCacheMiddleware")
        assert_pformat_equal(UpdateCacheMiddleware2, UpdateCacheMiddleware)

        with self.assertRaises(ImproperlyConfigured) as cm:
            get_attr_from_string("no point", "TEST")
        assert_pformat_equal(cm.exception.args[0], "no point isn't a TEST module")

        with self.assertRaises(ImproperlyConfigured) as cm:
            get_attr_from_string("django.core.doesntexists", "Foo Bar")
        assert_pformat_equal(
            cm.exception.args[0], 'Foo Bar module "django.core" does not define a "doesntexists" class'
        )

        with self.assertRaises(ImproperlyConfigured) as cm:
            get_attr_from_string("django_tools.utils.importlib.not_exists", "Import Lib")
        assert_pformat_equal(
            cm.exception.args[0],
            'Import Lib module "django_tools.utils.importlib" does not define a "not_exists" class',
        )

    def test_get_setting(self):
        assert_pformat_equal(get_setting("EMAIL_BACKEND"), "django.core.mail.backends.locmem.EmailBackend")

    @mock.patch("django_tools.utils.importlib.logger")
    def test_get_setting_not_exists(self, mock_logger):
        get_setting("DOESN'T EXISTS")
        mock_logger.debug.assert_called_with(""""DOESN'T EXISTS" not in settings defined""")

    @mock.patch("django_tools.utils.importlib.logger")
    @override_settings(STATIC_URL=None)
    def test_get_setting_empty(self, mock_logger):
        assert_pformat_equal(settings.STATIC_URL, None)
        get_setting("STATIC_URL")
        mock_logger.debug.assert_called_with("settings.STATIC_URL is None or empty")

    def test_get_attr_from_settings(self):
        obj = get_attr_from_settings("EMAIL_BACKEND", "email backend")
        self.assertIs(obj, EmailBackend)

    @mock.patch("django_tools.utils.importlib.logger")
    def test_get_attr_from_settings_not_exists(self, mock_logger):
        get_attr_from_settings("DOESN'T EXISTS", "a test")
        mock_logger.debug.assert_called_with(""""DOESN'T EXISTS" not in settings defined""")

    @mock.patch("django_tools.utils.importlib.logger")
    @override_settings(STATIC_URL=None)
    def test_get_attr_from_settings_empty(self, mock_logger):
        assert_pformat_equal(settings.STATIC_URL, None)
        get_attr_from_settings("STATIC_URL", "a test")
        mock_logger.debug.assert_called_with("settings.STATIC_URL is None or empty")

    def test_get_class_instance_from_settings(self):
        obj = get_class_instance_from_settings("EMAIL_BACKEND", "email backend")
        self.assertIsInstance(obj, EmailBackend)

    @mock.patch("django_tools.utils.importlib.logger")
    def test_get_class_instance_from_settings_not_exists(self, mock_logger):
        get_class_instance_from_settings("DOESN'T EXISTS", "a test")
        mock_logger.debug.assert_called_with(""""DOESN'T EXISTS" not in settings defined""")

    @mock.patch("django_tools.utils.importlib.logger")
    @override_settings(STATIC_URL=None)
    def test_get_class_instance_from_settings_empty(self, mock_logger):
        assert_pformat_equal(settings.STATIC_URL, None)
        get_class_instance_from_settings("STATIC_URL", "a test")
        mock_logger.debug.assert_called_with("settings.STATIC_URL is None or empty")
