
"""
    :created: 24.04.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.core.management import BaseCommand
from django.utils import translation

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.model_test_code_generator import ModelTestGenerator


class Command(BaseCommand):
    """
    List all models, e.g.:
        $ ./manage.py generate_model_test_code

    Generate test code, e.g.:
        $ ./manage.py generate_model_test_code auth
        $ ./manage.py generate_model_test_code auth.User
        $ ./manage.py generate_model_test_code cms.

    """
    help = "Generate unittest code for a model"

    def add_arguments(self, parser):
        parser.add_argument('model_label', nargs="?",
            help='Name of the Django model (can only be the first characters! We use "startwith"'
        )
        parser.add_argument('--translation', help='Language code that will be activated', default="en")
        parser.add_argument('--count', help='Number of data records to be generated.', type=int, default=2)

    def handle(self, *args, **options):
        model_label = options['model_label']
        language_code = options["translation"]
        count = int(options["count"])

        translation.activate(language_code)

        model_test_generator = ModelTestGenerator()

        if model_label is None:
            print("\nNo model_label given.\n")
            model_test_generator.print_all_plugins()
            return

        models = model_test_generator.get_models_startwith_label(model_label)
        if not models:
            print("\nERROR: No models starts with given label %r\n" % model_label)
            model_test_generator.print_all_plugins()
            return

        for model in models:
            queryset = model.objects.all()

            existing_count = queryset.count()
            if existing_count==0:
                print("#")
                print("# ERROR: %r is empty!" % model._meta.label)
                print("#")
                continue

            if existing_count<count:
                print("#")
                print("# Warning: They exists only %i items in %r!" % (existing_count, model._meta.label))
                print("#")

            queryset = queryset[:count]

            content = model_test_generator.from_queryset(queryset)
            print(content)
