"""
    :copyleft: 2017-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import os

from django.http import Http404
from django.test import SimpleTestCase
from django.test.utils import override_settings

# https://github.com/jedie/django-tools
import django_tools
from django_tools.filemanager.filesystem_browser import BaseFilesystemBrowser
from django_tools.unittest_utils.assertments import assert_pformat_equal


@override_settings(DEBUG=False)
class TestFilesystemBrowser(SimpleTestCase):
    """
    e.g.:
    https://en.wikipedia.org/wiki/Directory_traversal_attack
    """

    BASE_PATH = os.path.abspath(os.path.dirname(django_tools.__file__))

    def test_directory_traversal_attack1(self):
        try:
            BaseFilesystemBrowser(
                request=None, absolute_path=self.BASE_PATH, base_url="bar", rest_url="../"
            )
        except Http404 as err:
            assert_pformat_equal(str(err), "Directory doesn't exist!")

    @override_settings(DEBUG=True)
    def test_debug_message(self):
        sub_path = os.path.normpath(os.path.join(self.BASE_PATH, ".."))
        try:
            BaseFilesystemBrowser(
                request=None, absolute_path=self.BASE_PATH, base_url="bar", rest_url="../"
            )
        except Http404 as err:
            assert_pformat_equal(
                err.args[0].message,
                f"Directory '{sub_path}' is not in base path ('{self.BASE_PATH}')"
            )

    def test_directory_traversal_attack_encodings(self):
        rest_urls = (
            "/etc/passwd",
            "..",
            "../",
            "\\\\",
            # URI encoded directory traversal:
            "%2e%2e%2f",  # ../
            "%2e%2e/",  # ../
            "..%2f",  # ../
            "%2e%2e%5c",  # ..\
            # Unicode / UTF-8 encoded directory traversal:
            "..%c1%1c",  # ../
            "..%c0%af",  # ..\
            "%c0%ae%c0%ae%c1%1c",  # %c0%ae -> . -> ../
            "%c0%ae%c0%ae%c0%af",  # %c0%ae -> . -> ..\
        )
        for rest_url in rest_urls:
            # print(rest_url)
            try:
                BaseFilesystemBrowser(
                    request=None, absolute_path=self.BASE_PATH, base_url="bar", rest_url=rest_url
                )
            except Http404 as err:
                assert_pformat_equal(str(err), "Directory doesn't exist!")
