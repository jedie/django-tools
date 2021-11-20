import io

from django.core import management
from django.core.management.commands import makemigrations
from django.test import TestCase, override_settings


class TestMigrations(TestCase):
    @override_settings(MIGRATION_MODULES={})
    def test_missing_migrations(self):
        output = io.StringIO()
        try:
            management.call_command(
                makemigrations.Command(),
                dry_run=True,
                check_changes=True,
                verbosity=1,
                stdout=output
            )
        except SystemExit as err:
            if err.code != 0:
                raise AssertionError(output.getvalue())
