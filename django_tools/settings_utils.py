# coding: utf-8

"""
    utilities for settings.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from __future__ import absolute_import, division, print_function

from fnmatch import fnmatch


class InternalIps(list):
    """
    Allows you to use Unix shell-style wildcards of IP addresses in your INTERNAL_IPS.
    Used the fnmatch module.

    settings.py e.g.:
    --------------------------------------------------------------------------
    from django_tools.settings_utils import InternalIps

    INTERNAL_IPS = InternalIps(["127.0.0.1", "::1", "192.168.*.*", "10.0.*.*"])
    --------------------------------------------------------------------------

    borrowed from https://djangosnippets.org/snippets/1380/
    """
    def __contains__(self, key):
        for ip in self:
            if fnmatch(key, ip): return True
        return False

