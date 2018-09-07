# coding: utf-8

"""
    $ ./manage.py nice_diffsettings

    The code based on:
        django.core.management.commands.diffsettings
"""

from __future__ import absolute_import, unicode_literals, print_function

import pprint

from django.core.management.base import BaseCommand

def module_to_dict(module, omittable=lambda k: k.startswith('_')):
    """
    Same as django.core.management.commands.diffsettings.module_to_dict
    bur didn't use repr() ;)
    """
    return {k: v for k, v in module.__dict__.items() if not omittable(k)}


class Command(BaseCommand):
    help = """Displays differences between the current settings.py and Django's
    default settings in a pretty-printed representation."""

    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', dest='all', default=False,
            help='Display all settings, regardless of their value.')

    def handle(self, **options):
        from django.conf import settings, global_settings

        # Because settings are imported lazily, we need to explicitly load them.
        settings._setup()

        user_settings = module_to_dict(settings._wrapped)
        default_settings = module_to_dict(global_settings)

        self.stdout.write("-"*79)

        for key in sorted(user_settings):
            display = False
            if key not in default_settings:
                display = True
            elif user_settings[key] != default_settings[key]:
                display = True
            elif options['all']:
                display = True

            if display:
                self.stdout.write(
                    "%s = %s\n\n" % (key, pprint.pformat(user_settings[key]))
                )

        self.stdout.write("-" * 79)

