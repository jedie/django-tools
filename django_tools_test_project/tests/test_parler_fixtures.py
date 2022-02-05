"""
    :copyleft: 2017-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.test import TestCase
from django.utils import translation
from pprintpp import pprint

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools_test_project.django_tools_test_app.models import (
    SimpleParlerModel,
    generate_simple_parler_dummies,
)


class ParlerFixturesTestCase(TestCase):
    def set_setup(self):
        assert_pformat_equal(settings.LANGUAGES, (("de", "German"), ("en", "English")))

    def test_generate_simple_parler_dummies(self):
        generate_simple_parler_dummies()

        assert_pformat_equal(SimpleParlerModel.objects.all().count(), 5)

        with translation.override("en"):
            qs = SimpleParlerModel.objects.language(language_code="en").all()

            info = []
            for instance in qs:
                info.append((instance.slug, list(instance.get_available_languages())))

            pprint(info)

            # Every dummy entry should be translated in de and en:
            assert_pformat_equal(
                info,
                [
                    ("simpleparlermodel-en-1", ["de", "en"]),
                    ("simpleparlermodel-en-2", ["de", "en"]),
                    ("simpleparlermodel-en-3", ["de", "en"]),
                    ("simpleparlermodel-en-4", ["de", "en"]),
                    ("simpleparlermodel-en-5", ["de", "en"]),
                ],
            )

    # TODO:
    # def test_generate_parler_publisher_dummies(self):
    #     generate_parler_publisher_dummies()
    #
    #     assert_pformat_equal(ParlerPublisherModel.objects.all().count(), 5)
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
    #         assert_pformat_equal(info, [
    #             ('simpleparlermodel-en-1', ['de', 'en']),
    #             ('simpleparlermodel-en-2', ['de', 'en']),
    #             ('simpleparlermodel-en-3', ['de', 'en']),
    #             ('simpleparlermodel-en-4', ['de', 'en']),
    #             ('simpleparlermodel-en-5', ['de', 'en'])
    #         ])
