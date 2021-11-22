"""
    :created: 2015 by Jens Diemer
    :copyleft: 2015-2021 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging
import os
import shutil


log = logging.getLogger(__name__)


def find_executable(filename):
    path = shutil.which(filename, mode=os.F_OK)
    if not path:
        log.info('%s not found!', filename)
    else:
        log.info('%s found: "%s"', filename, path)
        if not os.access(path, os.X_OK):
            log.warning('%s is not executeable!', path)
        return path
