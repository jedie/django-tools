"""
    Display information about the logging setup

    created 06.09.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
from pprint import pprint

from django.conf import settings
from django.core.management.base import BaseCommand


log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    call via:
        $ ./manage.py logging_info
    """
    help = "Shows a list of all loggers and marks which ones are configured in settings.LOGGING"

    def handle(self, *args, **options):
        self.stdout.write("")
        self.stdout.write("_" * 79)
        self.stdout.write(self.help)
        self.stdout.write("")

        self.stdout.write("-" * 100)
        pprint(settings.LOGGING)
        self.stdout.write("-" * 100)

        for log_name in sorted(logging.Logger.manager.loggerDict.keys()):

            if log_name in settings.LOGGING["loggers"]:
                prefix = "\t[*]"
            else:
                prefix = "\t[ ]"

            self.stdout.write(f"{prefix}{log_name!r}")

        self.stdout.write('[ ] -> not configured in settings.LOGGING["loggers"]')
