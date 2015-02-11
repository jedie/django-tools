# coding: utf-8

"""
    exceptions for filemanager
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function



class FilemanagerError(Exception):
    """
    for errors with a message to staff/admin users.
    e.g.: Gallery filesystem path doesn't exist anymore.
    """
    pass


class DirectoryTraversalAttack(FilemanagerError):
    """
    Some unauthorized signs are found or the path is out of the base path.
    """
    pass