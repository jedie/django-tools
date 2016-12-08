#!/usr/bin/env python

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_tools_test_project.test_settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


def run_tests():
    import pytest
    errno = pytest.main(args=[])
    sys.exit(errno)


if __name__ == "__main__":
    main()
