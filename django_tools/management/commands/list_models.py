"""
    $ ./manage.py list_models

"""


from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Just list all existing models in app_label.ModelName format.'

    def handle(self, *args, **options):
        self.stdout.write("\nexisting models in app_label.ModelName format:\n\n")

        dotnames = []
        app_configs = apps.get_app_configs()
        for app_config in app_configs:
            app_label = app_config.label
            models = app_config.get_models()
            for model in models:
                dotnames.append(
                    f"{app_label}.{model._meta.object_name}"
                )

        for no, dotname in enumerate(sorted(dotnames), 1):
            self.stdout.write(f"{no:02d} - {dotname}\n")

        self.stdout.write("\nINSTALLED_APPS....: %i\n" % len(settings.INSTALLED_APPS))
        self.stdout.write("Apps with models..: %i\n\n" % len(app_configs))
