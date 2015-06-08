# coding: utf-8

"""
    utils for filemanager
    ~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function



import posixpath
import os
import ntpath


def clean_posixpath(path, up_level_references=False):
    """
    Based on code from:
    https://github.com/django/django/blob/master/django/views/static.py
    
    But we build always a posixpath with "/" as path separate character.  
    
    
    Keep starting/ending slash:
    
    >>> clean_posixpath("no/slash")
    'no/slash'
    >>> clean_posixpath("/starts/with/slash")
    '/starts/with/slash'
    >>> clean_posixpath("ends/with/slash/")
    'ends/with/slash/'
    >>> clean_posixpath("") # normpath would return: "."
    ''
    >>> clean_posixpath("/")
    '/'
    >>> clean_posixpath("/../")
    '/'


    Remove every crude characters:
    
    >>> clean_posixpath("foo//bar")
    'foo/bar'
    >>> clean_posixpath("/foo/./bar")
    '/foo/bar'
    >>> clean_posixpath(r"foo\\bar/")
    'foo/bar/'
    
    
    up-level references would be only applied if activated:
    
    >>> clean_posixpath("/foo/bar/../../etc/passwd") # normpath would return: '../etc/passwd'
    '/foo/bar/etc/passwd'
    >>> clean_posixpath("/foo/bar/../../etc/passwd", up_level_references=True)
    '/etc/passwd'
    
    >>> clean_posixpath("../../../etc/passwd") # normpath would return: '../../../etc/passwd'
    'etc/passwd'
    
    >>> clean_posixpath(r"\\foo\\bar\\..\\etc\\passwd") # normpath would return: '\\foo\\bar\\..\\etc\\password'
    '/foo/bar/etc/passwd'
    
    
    Ignore windows drive parts:
    
    >>> clean_posixpath(r"c:\\boot.ini")
    'boot.ini'
    >>> clean_posixpath(r"foo/bar/c:\\boot.ini")
    'foo/bar/boot.ini'
    """
    path = path.replace('\\', '/')

    add_slash = path.endswith("/")    
    if path.startswith("/"):
        newpath = "/"
    else:
        newpath = ""    
    path = path.strip("/")

    if up_level_references:
        # e.g.: foo/../bar -> bar
        path = posixpath.normpath(path)

    for part in path.split("/"):       
        if not part:
            # Strip empty path components.
            continue

        drive, part = ntpath.splitdrive(part)
        head, part = posixpath.split(part)
        if part in (".", ".."):
            continue
        newpath = posixpath.join(newpath, part)
        
    if add_slash and newpath != "/":
        newpath += "/"
        
    return newpath


def add_slash(path):
    """
    >>> add_slash("/foo")
    '/foo/'
    >>> add_slash("/bar/")
    '/bar/'
    """
    if not path.endswith(os.sep):
        path += os.sep
    return path    


def symbolic_notation(mode):
    """
    Convert os.stat().st_mode values to a symbolic representation. e.g: 
       
    >>> s = symbolic_notation(16893) # -> 040775 -> 775
    >>> s == 'rwxrwxr-x'
    True
    
    >>> s = symbolic_notation(33204) # -> 0100664 -> 664
    >>> s == 'rw-rw-r--'
    True
    """
    mode = mode & 0o777 # strip "meta info"
    chmod_symbol = ''.join(
        mode & 0o400 >> i and x or '-' for i, x in enumerate('rwxrwxrwx')
    )
    return chmod_symbol


if __name__ == "__main__":
    import doctest
    print(doctest.testmod(
#        verbose=True
        verbose=False
    ))