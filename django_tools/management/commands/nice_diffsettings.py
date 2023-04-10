"""
    Pretty version of Django's "diffsettings" using rich

    $ ./manage.py nice_diffsettings

    The code based on:
        django.core.management.commands.diffsettings
"""


from django_rich.management import RichCommand
from rich.highlighter import ReprHighlighter
from rich.pretty import pretty_repr


def module_to_dict(module, omittable=lambda k: k.startswith("_")):
    """
    Same as django.core.management.commands.diffsettings.module_to_dict
    but didn't use repr() ;)
    """
    return {k: v for k, v in module.__dict__.items() if not omittable(k)}


class Command(RichCommand):
    help = """Displays differences between the current settings.py and Django's
    default settings in a pretty-printed representation."""

    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            dest="all",
            default=False,
            help="Display all settings, regardless of their value.",
        )

    def handle(self, **options):
        from django.conf import global_settings, settings

        # Because settings are imported lazily, we need to explicitly load them.
        if not settings.configured:
            settings._setup()

        user_settings = module_to_dict(settings._wrapped)
        default_settings = module_to_dict(global_settings)

        highlighter = ReprHighlighter()

        self.console.print("-" * 79)

        for key in sorted(user_settings):
            display = False
            if key not in default_settings:
                display = True
            elif user_settings[key] != default_settings[key]:
                display = True
            elif options["all"]:
                display = True

            if display:

                value = user_settings[key]
                try:
                    pformated = pretty_repr(value, expand_all=True)
                    pformated = highlighter(pformated)
                except Exception as err:
                    # e.g.: https://github.com/andymccurdy/redis-py/issues/995
                    pformated = f"<Error: {err}>"

                self.console.print(f"{key} = {pformated}\n\n")

        self.console.print("-" * 79)
