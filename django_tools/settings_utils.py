# coding: utf-8

"""
    utilities for settings.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015-2017 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from __future__ import absolute_import, division, print_function

from fnmatch import fnmatch


class IpPattern(str):
    def __init__(self, pattern):
        self.pattern = pattern

    def __eq__(self, pat):
        """
        ALLOWED_HOSTS compares via "<ip> == ALLOWED_HOSTS"
        see: django.http.request.validate_host
        """
        return fnmatch(pat, self.pattern)

    def lower(self):
        return IpPattern(self.pattern.lower())

    def startswith(self, *args):
        return False

    def __str__(self):
        return self.pattern


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
    def __init__(self, pattern_list):
        super(FnMatchIps, self).__init__([IpPattern(pat) for pat in pattern_list])

    def __contains__(self, pat):
        # INTERNAL_IPS checks via "<ip> in INTERNAL_IPS"
        for ip in self:
            if pat == ip:
                return True
        return False


InternalIps = FnMatchIps # for compatibility
