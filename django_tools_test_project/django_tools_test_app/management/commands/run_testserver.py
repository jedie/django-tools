#!/usr/bin/env python3

import os
import sys
from pathlib import Path

from django.core.management import BaseCommand, call_command

from django_tools_test_project.django_tools_test_app import migrations as test_app_migrations


print("sys.real_prefix:", getattr(sys, "real_prefix", "-"))
print("sys.prefix:", sys.prefix)


class Command(BaseCommand):
    """
    Expand django.contrib.staticfiles runserver
    """
    help = "Setup test project and run django developer server"

    def verbose_call(self, command, *args, **kwargs):
        self.stderr.write("_" * 79)
        self.stdout.write(f"Call {command!r} with: {args!r} {kwargs!r}")
        call_command(command, *args, **kwargs)

    def handle(self, *args, **options):

        if "RUN_MAIN" not in os.environ:
            # RUN_MAIN added by auto reloader, see: django/utils/autoreload.py

            migration_path = Path(test_app_migrations.__file__).parent
            for file_path in migration_path.glob('*.py'):
                if file_path.name != '__init__.py':
                    self.stdout.write(f'Remove migration file: {file_path}')
                    file_path.unlink()

            self.verbose_call("makemigrations")  # helpfull for developming and add/change models ;)
            self.verbose_call("migrate")

            # django.contrib.staticfiles.management.commands.collectstatic.Command
            self.verbose_call("collectstatic", interactive=False, link=True)

        self.verbose_call("runserver", use_threading=False, use_reloader=True, verbosity=2)
