"""Test project for django-tools."""
import os
import sys


def start_test_project_server():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_tools_test_project.test_settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0], 'run_test_project_dev_server'])
