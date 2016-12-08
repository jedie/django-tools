# coding: utf-8

"""
    $ ./manage.py list_models

"""

from __future__ import absolute_import, unicode_literals, print_function


from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Just list all existing models as dot names.'

    def handle(self, *args, **options):
        self.stdout.write("\nexisting models as dot names:\n\n")

        model_count = 0
        app_configs = apps.get_app_configs()
        for app_config in app_configs:
            app_name = app_config.name
            models = app_config.get_models()
            for model in models:
                model_count += 1
                self.stdout.write("%02i - %s.models.%s\n" % (model_count, app_name, model._meta.object_name))

        self.stdout.write("\n%i INSTALLED_APPS\n" % len(settings.INSTALLED_APPS))
        self.stdout.write("%i apps with models\n\n" % len(app_configs))
