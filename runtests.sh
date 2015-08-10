#!/usr/bin/env bash

set -x

python manage.py test --verbosity=2 $*