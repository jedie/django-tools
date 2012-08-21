# coding: utf-8

"""
    filemanager
    ~~~~~~~~~~~

    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import posixpath
import urllib

if __name__ == "__main__":
    # For doctest only
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings
    global_settings.SITE_ID = 1

from django.http import Http404
from django.utils.translation import ugettext as _

from django_tools.filemanager.utils import add_slash, clean_posixpath
from django_tools.filemanager.exceptions import DirectoryTraversalAttack


class BaseFilesystemBrowser(object):
    """
    Base class for a django app like a filemanager, which contains only
    the base functionality to browse to a base path of the filesystem.
    
    >> fm = BaseFilesystemBrowser(None, BASE_PATH, "bar", "../etc/passwd")
    Traceback (most recent call last):
    ...
    DirectoryTraversalAttack: '..' found in '../etc/passwd'
        
    >> fm = BaseFilesystemBrowser(None, BASE_PATH, "bar", "///etc/passwd")
    Traceback (most recent call last):
    ...
    DirectoryTraversalAttack: '//' found in '///etc/passwd'
    
    >>> fm = BaseFilesystemBrowser(None, "/tmp/", "bar", "%c1%1c%c1%1c/etc/passwd")
    Traceback (most recent call last):
    ...
    Http404: Formed path '/tmp/\\xc1\\x1c\\xc1\\x1c/etc/passwd/' doesn't exist.
    
    >>> fm = BaseFilesystemBrowser(None, "/tmp/", "bar", "%c0%ae%c0%ae/etc/passwd")
    Traceback (most recent call last):
    ...
    Http404: Formed path '/tmp/\\xc0\\xae\\xc0\\xae/etc/passwd/' doesn't exist.
    """
    def __init__(self, request, absolute_path, base_url, rest_url):
        """
        absolute_path - path in filesystem to the root directory
        base_url - url prefix of this filemanager instance
        rest_url - relative sub path of the current view

        it is assumed that 'absolute_path' and 'base_url' are internal values
        and 'rest_url' are a external given value from the requested user.
        """
        self.request = request
        self.absolute_path = add_slash(absolute_path)
        self.base_url = clean_posixpath(base_url)

        rest_url = urllib.unquote(rest_url)
        rest_url = add_slash(rest_url)

        # To protect from directory traversal attack
        # https://en.wikipedia.org/wiki/Directory_traversal_attack
        clean_rest_url = clean_posixpath(rest_url)
        if clean_rest_url != rest_url:
            # path changed cause of "illegal" characters
            raise DirectoryTraversalAttack(
                "path %s is not equal to cleaned path: %s" % (repr(rest_url), repr(clean_rest_url))
            )

        self.rel_url = rest_url.lstrip("/")
        self.rel_path = add_slash(os.path.normpath(self.rel_url))

        self.abs_path = clean_posixpath(os.path.join(self.absolute_path, self.rel_path))
        self.check_path(self.absolute_path, self.abs_path)

        self.abs_url = posixpath.join(self.base_url, self.rel_url)

        if not os.path.isdir(self.abs_path):
            raise Http404("Formed path %r doesn't exist." % self.abs_path)

        self.breadcrumbs = self.build_breadcrumbs()

    def build_breadcrumbs(self):
        parts = ""
        url = self.base_url
        breadcrumbs = [{
            "name": _("index"),
            "title": _("goto 'index'"),
            "url": url
        }]
        rel_url = self.rel_url.strip("/")
        if not rel_url:
            return breadcrumbs

        for url_part in rel_url.split("/"):
            url += "%s/" % url_part
            parts += "%s/" % url_part
            breadcrumbs.append({
                "name": url_part,
                "title": _("goto '%s'") % parts.strip("/"),
                "url": url
            })
        return breadcrumbs

    def check_path(self, base_path, path):
        """
        Simple check if the path is a sub directory of base_path.
        This must be called from external!
        """
        # Important: the path must be terminated with a slash, otherwise:
        #
        # base_path = /foo/bar
        # path      = /foo/barNEW
        #
        # path starts with base_path without slashes
        #
        # which add slash:
        #
        # base_path = /foo/bar    -> /foo/bar/
        # path      = /foo/barNEW -> /foo/barNEW/
        #              doesn't start with ---^
        #
        assert base_path.endswith(os.sep), "'base_path' must ended with a slash!"
        assert path.endswith(os.sep), "'path' must ended with a slash!"

        if not path.startswith(base_path):
            raise DirectoryTraversalAttack("%r doesn't start with %r" % (path, base_path))

if __name__ == "__main__":
    import doctest
    print doctest.testmod(
#        verbose=True
        verbose=False
    )
