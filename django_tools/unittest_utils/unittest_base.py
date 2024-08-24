"""
    unittest base
    ~~~~~~~~~~~~~

    :copyleft: 2009-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import warnings

from django.test import TestCase
from django.urls import reverse

# https://github.com/jedie/django-tools
from django_tools.unittest_utils import assertments
from django_tools.unittest_utils.assertments import assert_equal_dedent, assert_in_dedent


class BaseUnittestCase(TestCase):
    """
    Extensions to plain Unittest TestCase

    TODO: move all assert methods to django_tools/unittest_utils/assertments.py
    """

    maxDiff = 3000

    def assertEqual_dedent(self, first, second, msg=""):
        warnings.warn(
            "Use django_tools.unittest_utils.assertments.assert_equal_dedent!", DeprecationWarning, stacklevel=2
        )
        assert_equal_dedent(first, second, msg=msg)

    def assertIn_dedent(self, member, container, msg=None):
        warnings.warn(
            "Use django_tools.unittest_utils.assertments.assert_in_dedent!", DeprecationWarning, stacklevel=2
        )
        assert_in_dedent(member, container)

    def assert_is_dir(self, path):
        warnings.warn("Use django_tools.unittest_utils.assertments.assert_is_dir!", DeprecationWarning, stacklevel=2)
        assertments.assert_is_dir(path)

    def assert_path_not_exists(self, path):
        warnings.warn(
            "Use django_tools.unittest_utils.assertments.assert_path_not_exists!", DeprecationWarning, stacklevel=2
        )
        assertments.assert_path_not_exists(path)

    def assert_is_file(self, path):
        warnings.warn("Use django_tools.unittest_utils.assertments.assert_is_file!", DeprecationWarning, stacklevel=2)
        assertments.assert_is_file(path)

    def assert_not_is_File(self, path):
        warnings.warn(
            "Use django_tools.unittest_utils.assertments.assert_path_not_exists!", DeprecationWarning, stacklevel=2
        )
        assertments.assert_path_not_exists(path)

    def assert_startswith(self, text, prefix):
        warnings.warn(
            "Use django_tools.unittest_utils.assertments.assert_startswith!", DeprecationWarning, stacklevel=2
        )
        assertments.assert_startswith(text, prefix)

    def assert_endswith(self, text, prefix):
        warnings.warn("Use django_tools.unittest_utils.assertments.assert_endswith!", DeprecationWarning, stacklevel=2)
        assertments.assert_endswith(text, prefix)

    def assert_exception_startswith(self, context_manager, text):
        """
        e.g.:

        with self.assertRaises(AssertionError) as cm:
            do_something()

        self.assert_exception_startswith(cm, "First part of the error message")
        """
        exception_text = context_manager.exception.args[0]
        if not exception_text.startswith(text):
            msg = f"{exception_text!r} doesn't starts with {text!r}"
            raise self.failureException(msg)

    def get_admin_url(self, obj, suffix):
        opts = obj._meta
        change_url = reverse(f"admin:{opts.app_label}_{opts.model_name}_{suffix}", args=(obj.pk,))
        return change_url

    def get_admin_change_url(self, obj):
        """
        Get the admin change url for the given model instance.
        e.g.:
            "/admin/<app_name>/<model_name>/<pk>/"
        """
        return self.get_admin_url(obj, suffix="change")

    def get_admin_add_url(self, obj):
        """
        Get the admin add url for the given model.
        e.g.:
            "/admin/<app_name>/<model_name>/add/"
        """
        opts = obj._meta
        change_url = reverse(f"admin:{opts.app_label}_{opts.model_name}_add")
        return change_url

    def get_messages(self, response):
        """
        Return all django message framwork entry as a normal list
        """
        return [str(message) for message in response.wsgi_request._messages]
