"""
    $ ./manage.py nice_diffsettings

    The code based on:
        django.core.management.commands.diffsettings
"""

import pprint

from django.core.management.base import BaseCommand


def module_to_dict(module, omittable=lambda k: k.startswith("_")):
    """
    Same as django.core.management.commands.diffsettings.module_to_dict
    but didn't use repr() ;)
    """
    return {k: v for k, v in module.__dict__.items() if not omittable(k)}


class Command(BaseCommand):
    help = """Displays differences between the current settings.py and Django's
    default settings in a pretty-printed representation."""

    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            dest="all",
            default=False,
            help="Display all settings, regardless of their value.",
        )

    def handle(self, **options):
        from django.conf import global_settings, settings

        # Because settings are imported lazily, we need to explicitly load them.
        settings._setup()

        user_settings = module_to_dict(settings._wrapped)
        default_settings = module_to_dict(global_settings)

        self.stdout.write("-" * 79)

        for key in sorted(user_settings):
            display = False
            if key not in default_settings:
                display = True
            elif user_settings[key] != default_settings[key]:
                display = True
            elif options["all"]:
                display = True

            if display:

                value = user_settings[key]
                try:
                    pformated = pprint.pformat(value)
                except Exception as err:
                    # e.g.: https://github.com/andymccurdy/redis-py/issues/995
                    pformated = f"<Error: {err}>"

                self.stdout.write(f"{key} = {pformated}\n\n")

        self.stdout.write("-" * 79)
