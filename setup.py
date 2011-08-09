#!/usr/bin/env python
# coding: utf-8

"""
    distutils setup
    ~~~~~~~~~~~~~~~

    :copyleft: 2009-2010 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys

from setuptools import setup, find_packages

from django_tools import VERSION_STRING


PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))


def get_authors():
    try:
        f = file(os.path.join(PACKAGE_ROOT, "AUTHORS"), "r")
        authors = [l.strip(" *\r\n") for l in f if l.strip().startswith("*")]
        f.close()
    except Exception, err:
        authors = "[Error: %s]" % err
    return authors


def get_long_description():
    fail_silently = sys.argv[1] not in ("--long-description", "sdist")
    try:
        f = file(os.path.join(PACKAGE_ROOT, "README.creole"), "r")
        desc_creole = f.read()
        f.close()

        desc_creole = unicode(desc_creole, 'utf-8').strip()

        from creole import creole2html, html2rest

        if fail_silently:
            from creole.shared.unknown_tags import transparent_unknown_nodes as unknown_emit
        else:
            from creole.shared.unknown_tags import raise_unknown_node as unknown_emit

        desc_html = creole2html(desc_creole)
        long_description = html2rest(desc_html,
            emitter_kwargs={"unknown_emit":unknown_emit}
        )
    except Exception, err:
        if not fail_silently:
            raise
        long_description = "[Error: %s]" % err

    return long_description


setup(
    name='django-tools',
    version=VERSION_STRING,
    description='miscellaneous tools for django',
    long_description=get_long_description(),
    author=get_authors(),
    maintainer="Jens Diemer",
    maintainer_email="django-tools@jensdiemer.de",
    url='http://code.google.com/p/django-tools/',
    packages=find_packages(),
    include_package_data=True, # include package data under svn source control
    zip_safe=False,
    classifiers=[
#        "Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",
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
