#!/bin/sh

# Interact with manage.py from our test project

exec poetry run python3 django_tools_test_project/manage.py "$@"
