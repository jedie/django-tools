import inspect
import os

from django.contrib.staticfiles.management.commands import collectstatic, runserver
from django.core.management import BaseCommand, call_command
from django.core.management.commands import makemigrations, migrate


class Command(BaseCommand):
    """
    Helper for easier development, by setup a local dev. server.

    Starts the django.contrib.staticfiles runserver, so no extra static files handling must
    be inserted into dev. urls.py ;)
    """

    help = "Setup test project and run django developer server"

    CALL_MAKEMIGRATIONS = True
    CALL_MIGRATE = True
    CALL_COLLECTSTATIC = True

    def verbose_call(self, command, *args, **kwargs):
        assert inspect.ismodule(command)
        command_name = command.__name__
        command_name = command_name.rsplit('.', 1)[-1]

        info = f'Call {command_name!r}'
        if args or kwargs:
            info += ' with:'
        if args:
            info += f' {args!r}'
        if kwargs:
            info += f' {kwargs!r}'

        self.stderr.write('_' * 79)
        self.stdout.write(info)

        command = command.Command()
        call_command(command, *args, **kwargs)

    def pre_setup(self) -> None:
        """
        May be overwritten with own logic.
        """
        pass

    def post_setup(self) -> None:
        """
        May be overwritten with own logic.
        """
        pass

    def setup(self) -> None:
        """
        May be overwritten with own logic.
        """
        if self.CALL_MAKEMIGRATIONS:
            # helpfull for developing and add/change models ;)
            self.verbose_call(makemigrations)

        if self.CALL_MIGRATE:
            self.verbose_call(migrate)

        if self.CALL_COLLECTSTATIC:
            # django.contrib.staticfiles.management.commands.collectstatic.Command
            self.verbose_call(collectstatic, interactive=False, link=True)

    def handle(self, *args, **options):

        if "RUN_MAIN" not in os.environ:
            # RUN_MAIN added by auto reloader, see: django/utils/autoreload.py
            self.pre_setup()
            self.setup()
            self.post_setup()

        self.verbose_call(runserver, use_threading=False, use_reloader=True, verbosity=2)
