

class DisableMigrations(object):
    """
    Speedup test run start by disable migrations, just create the database tables ;)

    Usage in test settings.py:

    from django_tools.unittest_utils.disable_migrations import DisableMigrations
    MIGRATION_MODULES = DisableMigrations()
    """
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"