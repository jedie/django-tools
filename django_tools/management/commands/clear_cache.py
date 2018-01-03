# coding: utf-8

"""
    'clear django cache' manage command


    setup:

        INSTALLED_APPS = [
            ...
            'django_tools',
            ...
        ]


    usage:

        $ ./manage.py clear_cache


    :copyleft: 2017 by the django-tools team, see AUTHORS for more details.
    :created: 2017 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.core.cache import caches
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Clears the complete Django cache."

    def handle(self, *args, **options):
        self.stdout.write("\nClear caches:\n")
        for cache in caches.all():
            self.stdout.write("\tClear '%s'\n" % cache.__class__.__name__)
            cache.clear()

        self.stdout.write("\ndone.\n")
