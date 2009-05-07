#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    distutils setup
    ~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2009 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys

from setuptools import setup, find_packages

from django_tools import VERSION_STRING


def get_authors():
    authors = []
    f = file("AUTHORS", "r")
    for line in f:
        if line.startswith('*'):
            authors.append(line[1:].strip())
    f.close()
    return authors

def get_long_description():
    f = file("README", "r")
    long_description = f.read()
    f.close()
    long_description.strip()
    return long_description


setup(
    name='django-tools',
    version=VERSION_STRING,
    description='miscellaneous tools for django',
    long_description = get_long_description(),
    author = get_authors(),
    maintainer = "Jens Diemer",
    url='http://code.google.com/p/django-tools/',
    packages=find_packages(),
    include_package_data=True, # include package data under svn source control
    zip_safe=False,
    classifiers = [
        "Development Status :: 4 - Beta",
#        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
#        "Intended Audience :: Education",
#        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        'Framework :: Django',
        "Topic :: Database :: Front-Ends",
        "Topic :: Documentation",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Operating System :: OS Independent",
    ]
)
