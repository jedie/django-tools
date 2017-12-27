# coding: utf-8

"""
    update_permissions manage command
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    setup:

        INSTALLED_APPS = [
            ...
            'django_tools',
            ...
        ]


    usage:

        $ ./manage.py update_permissions


    :copyleft: 2017 by the django-tools team, see AUTHORS for more details.
    :created: 2017 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.core.management.base import BaseCommand
from django.apps import apps
from django.contrib.auth.management import create_permissions


class Command(BaseCommand):
    help = "Create missing permissions for all app models."

    def handle(self, *args, **options):
        self.stdout.write("Create permissions for:")

        verbosity=int(options.get('verbosity', 0))
        app_configs = apps.get_app_configs()
        for app_config in app_configs:
            app_label = app_config.label
            self.stdout.write(" * %s" % app_label)
            create_permissions(app_config, verbosity=verbosity)
