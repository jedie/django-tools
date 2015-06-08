import os
from django.http import Http404
from django.test import SimpleTestCase
import django_tools
from django_tools.filemanager.exceptions import DirectoryTraversalAttack
from django_tools.filemanager.filesystem_browser import BaseFilesystemBrowser


class TestFilesystemBrowser(SimpleTestCase):
    """
    e.g.:
    https://en.wikipedia.org/wiki/Directory_traversal_attack
    """
    BASE_PATH=os.path.abspath(os.path.dirname(django_tools.__file__))

    def test_directory_traversal_attack1(self):
        self.assertRaises(DirectoryTraversalAttack,
            BaseFilesystemBrowser,
            request=None, absolute_path=self.BASE_PATH, base_url="bar", rest_url="../etc/passwd"
        )

    def test_directory_traversal_attack2(self):
        self.assertRaises(DirectoryTraversalAttack,
            BaseFilesystemBrowser,
            request=None, absolute_path=self.BASE_PATH, base_url="bar", rest_url="///etc/passwd"
        )

    def test_directory_traversal_attack3(self):
        self.assertRaises(DirectoryTraversalAttack,
            BaseFilesystemBrowser,
            request=None, absolute_path=self.BASE_PATH, base_url="bar", rest_url="\etc\passwd"
        )

    def test_directory_traversal_attack_encodings(self):
        parts = (
            # URI encoded directory traversal:
            "%2e%2e%2f", # ../
            "%2e%2e/", # ../
            "..%2f", # ../
            "%2e%2e%5c", # ..\

            # Unicode / UTF-8 encoded directory traversal:
            "..%c1%1c", # ../
            "..%c0%af", # ..\
            "%c0%ae", # .
        )
        for part in parts:
            rest_url="%setc/passwd" % part
            # print(rest_url)
            self.assertRaises(DirectoryTraversalAttack,#Http404,
                BaseFilesystemBrowser,
                request=None, absolute_path=self.BASE_PATH, base_url="bar", rest_url=rest_url
            )
