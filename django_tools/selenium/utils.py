"""
    :created: 2015 by Jens Diemer
    :copyleft: 2015-2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)


def find_executable(filename, extra_search_paths=None):
    """
    >>> find_executable("not existsing file", ["/foo", "/bar"])
    Traceback (most recent call last):
        ...
    FileNotFoundError: Can't find 'not existsing file' in PATH or ['/foo', '/bar']!

    >>> path = find_executable("python")
    >>> path.is_file()
    True
    """
    path = os.environ["PATH"]
    paths = path.split(os.pathsep)

    if extra_search_paths:
        paths += list(extra_search_paths)

    for path in paths:
        path = Path(path, filename)
        if path.is_file():
            if not os.access(str(path), os.X_OK):
                raise FileNotFoundError("%s exists, but it's not executable!" % path)
            return path

    raise FileNotFoundError("Can't find %r in PATH or %s!" % (filename, extra_search_paths))
