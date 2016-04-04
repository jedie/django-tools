# coding: utf-8

"""
    unittests for filemanager
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import os
import unittest
import tempfile

if __name__ == "__main__":
    # For doctest only
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings
    global_settings.SITE_ID = 1

from django.http import Http404

from django_tools.filemanager.filemanager import BaseFilemanager
from django_tools.filemanager.exceptions import DirectoryTraversalAttack


class FilemanagerBaseTestCase(unittest.TestCase):
    """
    Create this test filesystem tree:

    self.BASE_PATH/file1.txt
    self.BASE_PATH/file2.txt
    self.BASE_PATH/subdir1/subfile1.txt
    self.BASE_PATH/subdir1/subsubdir1/
    self.BASE_PATH/subdir1/subsubdir1/subsubfile1.txt
    self.BASE_PATH/subdir1/subsubdir1/subsubfile2.txt
    self.BASE_PATH/subdir1/emptysubsubdir/
    self.BASE_PATH/emptysubdir/
    """
    @classmethod
    def setUpClass(cls):
        super(FilemanagerBaseTestCase, cls).setUpClass()
        cls.BASE_PATH = "%s/" % tempfile.mkdtemp(prefix="filemanager-unittests_")

        # For dir traversal attack tests
        cls.SUB_BASE_PATH = os.path.join(cls.BASE_PATH, "subdir1")
        cls.ATTACK_PARTS = ("..", "..\\", "../",
            # from https://en.wikipedia.org/wiki/Directory_traversal_attack#URI_encoded_directory_traversal
            "%2e%2e%2f", "%2e%2e/", "..%2f", "%2e%2e%5c"
            # from https://en.wikipedia.org/wiki/Directory_traversal_attack#Unicode_.2F_UTF-8_encoded_directory_traversal
            "..%c1%1c", "..%c0%af",
            "..\xc1\x1c", "..\xc0\xaf",
        )

        cls.DIRS = (
            (cls.BASE_PATH, "subdir1", "subsubdir1"),
            (cls.BASE_PATH, "subdir1", "emptysubsubdir"),
            (cls.BASE_PATH, "emptysubdir"),
        )
        cls.FILES = (
            (cls.BASE_PATH, "file1.txt"),
            (cls.BASE_PATH, "file2.txt"),
            (cls.BASE_PATH, "subdir1", "subfile1.txt"),
            (cls.BASE_PATH, "subdir1", "subsubdir1", "subsubfile1.txt"),
            (cls.BASE_PATH, "subdir1", "subsubdir1", "subsubfile2.txt"),
        )

        # Create dirs:
        for dirs in cls.DIRS:
            path = os.path.join(*dirs)
#            print "Create dir: %s" % repr(path)
            os.makedirs(path)

        # Create files:
        for file_info in cls.FILES:
            path = os.path.join(*file_info)
            content = "File content for: %s" % repr(file_info[-1])
#            print "Create file %s with %s" % (repr(path), repr(content))
            with open(path, "w") as f:
                f.write(content)

    @classmethod
    def tearDownClass(cls):
        super(FilemanagerBaseTestCase, cls).tearDownClass()
        tempdir = tempfile.gettempdir()
        if cls.BASE_PATH.startswith(tempdir):
            for root, dirs, files in os.walk(cls.BASE_PATH, topdown=False):
                for name in files:
                    path = os.path.join(root, name)
                    os.remove(path)
                for name in dirs:
                    path = os.path.join(root, name)
                    os.rmdir(path)
            os.rmdir(cls.BASE_PATH)
        else:
            cls.fail("Cleanup error: %s not in %s" % (cls.BASE_PATH, tempdir))

    def test_setup(self):
        """ if this tests fails, all other may fail, too. """
        for file_info in self.FILES:
            path = os.path.join(*file_info)
            self.failUnless(os.path.isfile(path))


class FilemanagerDirectoryTraversal(FilemanagerBaseTestCase):

    def test_subdir1(self):
        subdir = "subdir1"
        base_url = "/base/url/"
        rest_url = "%s/" % subdir
        fm = BaseFilemanager(None, self.BASE_PATH, base_url, rest_url)
        self.assertEqual(fm.abs_url, '/base/url/subdir1/')
        self.assertEqual(fm.absolute_path, self.BASE_PATH)
        self.assertEqual(fm.breadcrumbs, [
            {'url': base_url, 'name': 'index', 'title': "goto 'index'"},
            {'url': '/base/url/%s/' % subdir, 'name': subdir, 'title': "goto '%s'" % subdir}
        ])

    def test_not_existing_path1(self):
        self.assertRaises(Http404,
            BaseFilemanager, None, self.BASE_PATH, "/base/url/", "not_exists"
        )
    def test_not_existing_path2(self):
        self.assertRaises(Http404,
            BaseFilemanager, None, self.BASE_PATH, "/base/url/", "does/not/exists"
        )

    def test_dir_traversal_attack1(self):
        for parts in self.ATTACK_PARTS:
            self.assertRaises((DirectoryTraversalAttack, Http404),
                BaseFilemanager, None, self.SUB_BASE_PATH, "/base/url/", parts,
            )

    def test_dir_traversal_attack2(self):
        for parts in self.ATTACK_PARTS:
            self.assertRaises((DirectoryTraversalAttack, Http404),
                BaseFilemanager, None, self.SUB_BASE_PATH, "/base/url/", "%semptysubdir" % parts,
            )

    def test_dir_traversal_attack3(self):
        self.assertRaises(Http404,
            BaseFilemanager, None, self.BASE_PATH, "/base/url/", "subdir1/../../etc/passwd"
        )

    def test_dir_traversal_attack4(self):
        self.assertRaises(Http404,
            BaseFilemanager, None, self.BASE_PATH, "/base/url/", "subdir1/c:\\boot.ini"
        )


if __name__ == '__main__':
    unittest.main()
