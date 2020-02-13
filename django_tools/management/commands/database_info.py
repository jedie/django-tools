"""
    database_info manage command


    setup:

        INSTALLED_APPS = [
            ...
            'django_tools',
            ...
        ]


    usage:

        $ ./manage.py database_info


    :copyleft: 2017 by the django-tools team, see AUTHORS for more details.
    :created: 2017 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pprint import pprint

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = "Information about the used database and connections"

    def handle(self, *args, **options):
        self.stdout.write("")
        self.stdout.write("_" * 79)
        self.stdout.write(self.help)
        self.stdout.write("")

        # self.stdout.write("settings.DATABASES = ", ending="")
        # pprint(settings.DATABASES)
        # self.stdout.write("-"*79)

        for alias, settings_dict in settings.DATABASES.items():
            self.stdout.write(f"Database alias {alias!r}:")
            self.stdout.write("")
            engine = settings_dict["ENGINE"]
            engine = engine.rsplit(".", 1)[-1]
            self.stdout.write(f"engine...............: {engine!r}")
            if engine == "sqlite3":
                # https://docs.python.org/3/library/sqlite3.html#module-functions-and-constants
                import sqlite3
                self.stdout.write(f"sqlite lib version...: {sqlite3.sqlite_version!r}")
                self.stdout.write(f"sqlite module version: {sqlite3.version!r}")

            self.stdout.write(f"name.................: {settings_dict['NAME']!r}")
            self.stdout.write(f"user.................: {settings_dict['USER']!r}")
            self.stdout.write(f"host.................: {settings_dict['HOST']!r}")
            self.stdout.write(f"port.................: {settings_dict['PORT']!r}")

        connection_list = connections.all()

        self.stdout.write("")
        self.stdout.write("There are %i connections." % len(connection_list))

        for no, conn in enumerate(connection_list, 1):
            self.stdout.write("")
            self.stdout.write(f"connection {no:d} alias: {conn.alias!r} settings_dict:")
            pprint(conn.settings_dict)

        self.stdout.write("")
        self.stdout.write("-" * 79)
