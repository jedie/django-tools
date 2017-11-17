# coding: utf-8

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
        self.stdout.write("_"*79)
        self.stdout.write(self.help)
        self.stdout.write("")

        # self.stdout.write("settings.DATABASES = ", ending="")
        # pprint(settings.DATABASES)
        # self.stdout.write("-"*79)

        for alias, settings_dict in settings.DATABASES.items():
            self.stdout.write("Database alias %r:" % alias)
            self.stdout.write("")
            engine = settings_dict["ENGINE"]
            engine = engine.rsplit(".",1)[-1]
            self.stdout.write("engine...............: %r" % engine)
            if engine == "sqlite3":
                # https://docs.python.org/3/library/sqlite3.html#module-functions-and-constants
                import sqlite3
                self.stdout.write("sqlite lib version...: %r" % sqlite3.sqlite_version)
                self.stdout.write("sqlite module version: %r" % sqlite3.version)

            self.stdout.write("name.................: %r" % settings_dict["NAME"])
            self.stdout.write("user.................: %r" % settings_dict["USER"])
            self.stdout.write("host.................: %r" % settings_dict["HOST"])
            self.stdout.write("port.................: %r" % settings_dict["PORT"])

        connection_list = connections.all()

        self.stdout.write("")
        self.stdout.write("There are %i connections." % len(connection_list))

        for no, conn in enumerate(connection_list, 1):
            self.stdout.write("")
            self.stdout.write("connection %i alias: %r settings_dict:" % (no, conn.alias))
            pprint(conn.settings_dict)

        self.stdout.write("")
        self.stdout.write("-"*79)
