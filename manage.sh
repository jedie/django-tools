#!/bin/sh

# Interact with manage.py from our test project

export DJANGO_SETTINGS_MODULE=django_tools_test_project.settings.local

exec poetry run python3 django_tools_test_project/manage.py "$@"
