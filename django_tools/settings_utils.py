# coding: utf-8

"""
    utilities for settings.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015-2017 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from __future__ import absolute_import, division, print_function

from fnmatch import fnmatch


class FnMatchIps(list):
    """
    Allows you to use Unix shell-style wildcards of IP addresses
    for settings.INTERNAL_IPS and settings.ALLOWED_HOSTS
    used the fnmatch module.

    settings.py e.g.:
    --------------------------------------------------------------------------
    from django_tools.settings_utils import FnMatchIps

    INTERNAL_IPS = FnMatchIps(["127.0.0.1", "::1", "192.168.*.*", "10.0.*.*"])
    ALLOWED_HOSTS = FnMatchIps(["127.0.0.1", "::1", "192.168.*.*", "10.0.*.*"])
    --------------------------------------------------------------------------

    borrowed from https://djangosnippets.org/snippets/1380/
    """
    def _fnmatch(self, pat):
        for ip in self:
            if fnmatch(pat, ip): return True
        return False

    __eq__ = _fnmatch # ALLOWED_HOSTS compares, see: django.http.request.validate_host
    __contains__ = _fnmatch # INTERNAL_IPS


InternalIps = FnMatchIps # for compatibility
