import inspect
import os

from django.contrib.staticfiles.management.commands import runserver
from django.core.management import call_command
from django.core.management.commands import makemigrations, migrate
from django.core.management.commands.runserver import Command as BaseCommand


class Command(BaseCommand):
    """
    Helper for easier development, by setup a local dev. server.

    Starts the django.contrib.staticfiles runserver, so no extra static files handling must
    be inserted into dev. urls.py ;)
    """

    help = "Setup test project and run django developer server"

    def verbose_call(self, command, verbose=True, **kwargs):
        assert inspect.ismodule(command)

        if verbose:
            command_name = command.__name__
            command_name = command_name.rsplit('.', 1)[-1]

            info = f'Call "{self.style.SQL_FIELD(command_name)}"'
            if kwargs:
                for k, v in sorted(kwargs.items()):
                    if v is not None:
                        info += f' {self.style.SQL_KEYWORD(k)}:{v!r}'

            self.stdout.write('\n')
            self.stdout.write(self.style.WARNING('_' * 79))
            self.stdout.write(info)
            self.stdout.write('\n')

        # Sub command should use the same stdout/err:
        kwargs.update(
            dict(
                stdout=self.stdout,
                stderr=self.stderr,
            )
        )

        command = command.Command()
        call_command(command, **kwargs)

    def pre_setup(self, **options) -> None:
        """
        May be overwritten with own logic.
        """
        pass

    def post_setup(self, **options) -> None:
        """
        May be overwritten with own logic.
        """
        pass

    def setup(self, call_migrate=True, call_makemigrations=True) -> None:
        """
        May be overwritten with own logic.
        """
        if call_makemigrations:
            # helpful for developing and add/change models ;)
            self.verbose_call(makemigrations)

        if call_migrate:
            self.verbose_call(migrate)

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--nomakemigrations',
            action='store_false',
            dest='call_makemigrations',
            help='Do not run "makemigrations" in setup step',
        )
        parser.add_argument(
            '--nomigrate',
            action='store_false',
            dest='call_migrate',
            help='Do not run "migrate" in setup step',
        )

    def handle(self, **options):

        # RUN_MAIN added by auto reloader, see: django/utils/autoreload.py
        run_main = "RUN_MAIN" in os.environ

        setup_kwargs = {
            'call_makemigrations': options.pop('call_makemigrations'),
            'call_migrate': options.pop('call_migrate'),
        }

        if not run_main:
            self.pre_setup(**options)
            self.setup(**setup_kwargs)
            self.post_setup(**options)

        self.verbose_call(
            runserver,  # <<< the staticfiles server!
            #
            # Will be called two times, for autoreload,
            # be verbose only one time:
            verbose=not run_main,
            **options,
        )
