# coding: utf-8

"""
    filemanager
    ~~~~~~~~~~~

    :copyleft: 2012-2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import os
import posixpath

from django.utils.six.moves import urllib
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import Http404
from django.utils.translation import ugettext as _

from django_tools.filemanager.utils import add_slash, clean_posixpath
from django_tools.filemanager.exceptions import DirectoryTraversalAttack
from django_tools.validators import ExistingDirValidator

STOP_PARTS = (
    # https://en.wikipedia.org/wiki/Directory_traversal_attack#Unicode_.2F_UTF-8_encoded_directory_traversal
    "%c1%1c", # %c1%1c can be translated to /
    "%c0%af", # %c0%af can be translated to \
    "%c0%ae", # %c0%af can be translated to .
)

class BaseFilesystemBrowser(object):
    """
    Base class for a django app like a filemanager, which contains only
    the base functionality to browse to a base path of the filesystem.
    """
    def __init__(self, request, absolute_path, base_url, rest_url):
        """
        absolute_path - path in filesystem to the root directory
        base_url - url prefix of this filemanager instance
        rest_url - relative sub path of the current view

        it is assumed that 'absolute_path' and 'base_url' are internal values
        and 'rest_url' are a external given value from the requested user.

        TODO: Use django_tools.validators.ExistingDirValidator and merge code!
        """
        self.request = request
        self.absolute_path = add_slash(absolute_path)
        self.base_url = clean_posixpath(base_url)

        self.dir_validator = ExistingDirValidator(self.absolute_path)

        rest_url = add_slash(rest_url)
        try:
            self.dir_validator(rest_url)
        except ValidationError as err:
            if settings.DEBUG:
                raise Http404(err)
            else:
                raise Http404(_("Directory doesn't exist!"))

        self.rel_url = posixpath.normpath(rest_url).lstrip("/")
        self.abs_url = posixpath.join(self.base_url, rest_url)
        if not os.path.isdir(self.absolute_path):
            if settings.DEBUG:
                raise Http404(
                    "Formed path %r doesn't exist." % self.absolute_path)
            else:
                raise Http404(_("Directory doesn't exist!"))

        # # print("rest_url 1: %r" % rest_url)
        # for part in STOP_PARTS:
        #     if part in rest_url:
        #         raise DirectoryTraversalAttack("Stop chars %r found!" % part)
        #
        # rest_url = urllib.parse.unquote(rest_url)
        # # print("rest_url 2: %r" % rest_url)
        #
        #
        #
        # # To protect from directory traversal attack
        # # https://en.wikipedia.org/wiki/Directory_traversal_attack
        # clean_rest_url = clean_posixpath(rest_url)
        # if clean_rest_url != rest_url:
        #     # path changed cause of "illegal" characters
        #     raise DirectoryTraversalAttack(
        #         "path %s is not equal to cleaned path: %s" % (repr(rest_url), repr(clean_rest_url))
        #     )
        #
        # self.rel_url = rest_url.lstrip("/")
        # self.rel_path = add_slash(os.path.normpath(self.rel_url))
        #
        # self.abs_path = clean_posixpath(os.path.join(self.absolute_path, self.rel_path))
        # self.check_path(self.absolute_path, self.abs_path)
        #
        # self.abs_url = posixpath.join(self.base_url, self.rel_url)
        #
        # if not os.path.isdir(self.abs_path):
        #     raise Http404("Formed path %r doesn't exist." % self.abs_path)

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


