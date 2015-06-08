#!/usr/bin/env python
# coding: utf-8

"""
    run unittests
    ~~~~~~~~~~~~~

    run all tests:

    ./runtests.py

    run only some tests, e.g.:

    ./runtests.py tests.test_file
    ./runtests.py tests.test_file.test_class
    ./runtests.py tests.test_file.test_class.test_method

    :copyleft: 2015 by the django-tools team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function

import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def run_unittests(test_labels=None):
    django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(
        verbosity=2,
        # failfast=True,
    )

    if test_labels is None or test_labels == ["test"]:
        test_labels = ['tests']

    # First: Import test test labels, because we will see
    # a normal import error traceback.
    # Tracebacks from run_tests() are a little bit confuse.
    for label in test_labels:
        __import__(label)

    failures = test_runner.run_tests(test_labels)

    sys.exit(bool(failures))


def cli_run():
    os.environ['DJANGO_SETTINGS_MODULE'] = os.environ.get('DJANGO_SETTINGS_MODULE', "django_tools_test_project.test_settings")

    if "-v" in sys.argv or "--verbosity" in sys.argv:
        print("DJANGO_SETTINGS_MODULE=%r" % os.environ['DJANGO_SETTINGS_MODULE'])

    run_unittests(test_labels=sys.argv[1:])


if __name__ == "__main__":
    cli_run()


