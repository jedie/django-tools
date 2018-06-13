#!/usr/bin/env python3

import os
import sys

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.management.commands.runserver import Command as RunServerCommand
from django.core.management import call_command

print("sys.real_prefix:", getattr(sys, "real_prefix", "-"))
print("sys.prefix:", sys.prefix)



class Command(RunServerCommand):
    """
    Expand django.contrib.staticfiles runserver
    """
    help = "Setup test project and run django developer server"

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument("--fresh", action="store_true", dest="delete_first", default=False,
            help="Delete existing entries.")

    def verbose_call(self, command, *args, **kwargs):
        self.stderr.write("_"*79)
        self.stdout.write("Call %r with: %r %r" % (command, args, kwargs))
        call_command(command, *args, **kwargs)

    def handle(self, *args, **options):

        delete_first=options.get('delete_first')

        if "RUN_MAIN" not in os.environ:
            # RUN_MAIN added by auto reloader, see: django/utils/autoreload.py
            self.verbose_call("makemigrations") # helpfull for developming and add/change models ;)
            self.verbose_call("migrate")

            # django.contrib.staticfiles.management.commands.collectstatic.Command
            self.verbose_call("collectstatic", interactive=False, link=True)

            User=get_user_model()
            qs = User.objects.filter(is_active = True, is_superuser=True)
            if qs.count() == 0:
                self.verbose_call("createsuperuser")

        options["insecure_serving"] = True
        super(Command, self).handle(*args, **options)
