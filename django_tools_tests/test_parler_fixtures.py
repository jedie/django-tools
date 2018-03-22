from pprint import pprint

from django.conf import settings
from django.test import TestCase
from django.utils import translation

from django_tools_test_project.django_tools_test_app.models import generate_simple_parler_dummies, SimpleParlerModel


class ParlerFixturesTestCase(TestCase):
    def set_setup(self):
        self.assertEqual(settings.LANGUAGES, (('de', 'German'), ('en', 'English')))

    def test_generate_simple_parler_dummies(self):
        generate_simple_parler_dummies()

        self.assertEqual(SimpleParlerModel.objects.all().count(), 5)

        with translation.override("en"):
            qs = SimpleParlerModel.objects.language(language_code="en").all()

            info = []
            for instance in qs:
                info.append(
                    (instance.slug, list(instance.get_available_languages()))
                )

            pprint(info)

            # Every dummy entry should be translated in de and en:
            self.assertEqual(info, [
                ('simpleparlermodel-en-1', ['de', 'en']),
                ('simpleparlermodel-en-2', ['de', 'en']),
                ('simpleparlermodel-en-3', ['de', 'en']),
                ('simpleparlermodel-en-4', ['de', 'en']),
                ('simpleparlermodel-en-5', ['de', 'en'])
            ])

    # TODO:
    # def test_generate_parler_publisher_dummies(self):
    #     generate_parler_publisher_dummies()
    #
    #     self.assertEqual(ParlerPublisherModel.objects.all().count(), 5)
    #
    #     with translation.override("en"):
    #         qs = ParlerPublisherModel.objects.language(language_code="en").all().published()
    #
    #         info = []
    #         for instance in qs:
    #             info.append(
    #                 (instance.slug, list(instance.get_available_languages()))
    #             )
    #
    #         pprint(info)
    #
    #         # Every dummy entry should be translated in de and en:
    #         self.assertEqual(info, [
    #             ('simpleparlermodel-en-1', ['de', 'en']),
    #             ('simpleparlermodel-en-2', ['de', 'en']),
    #             ('simpleparlermodel-en-3', ['de', 'en']),
    #             ('simpleparlermodel-en-4', ['de', 'en']),
    #             ('simpleparlermodel-en-5', ['de', 'en'])
    #         ])
