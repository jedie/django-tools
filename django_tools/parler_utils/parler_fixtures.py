
"""
    :created: 22.03.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.conf import settings
from django.utils.text import slugify

# https://github.com/jedie/django-tools
from django_tools.fixture_tools.languages import iter_languages

log = logging.getLogger(__name__)


class ParlerDummyGenerator:
    """
    Helper to generate dummies for Parler models.
    """
    languages = settings.LANGUAGES # Languages for created content.
    default_language_code = settings.LANGUAGE_CODE # First language to start create

    def __init__(self, ParlerModelClass, publisher_model=False, unique_translation_field="slug"):
        self.ParlerModelClass = ParlerModelClass
        self.class_name = ParlerModelClass.__name__
        self.publisher_model = publisher_model # ParlerModelClass is sub class from PublisherModelBase) ?
        self.unique_translation_field = unique_translation_field

    def get_unique_translation_field_value(self, no, language_code):
        """
        Intended to be overwritten.
        """
        return slugify(
            "%s %s %i" % (self.class_name, language_code, no)
        )

    def add_instance_values(self, instance, language_code, lang_name, no):
        """
        Intended to be overwritten.
        """
        return instance

    def _get_lookup_kwargs(self, language_code, translation_field_value):
        lookup_kwargs = {
            "translations__language_code": language_code,
            "translations__%s" % self.unique_translation_field: translation_field_value
        }
        if self.publisher_model:
            # Is a Publisher model: filter drafts only:
            lookup_kwargs["publisher_is_draft"] = True

        return lookup_kwargs

    def get_or_create(self, count):
        for no in range(1,count+1):
            self._get_or_create(no=no)

    def _get_or_create(self, no):
        translation_field_value = self.get_unique_translation_field_value(no, language_code=self.default_language_code)

        lookup_kwargs = self._get_lookup_kwargs(
            language_code=self.default_language_code,
            translation_field_value=translation_field_value
        )

        qs = self.ParlerModelClass.objects.language(language_code=self.default_language_code)
        instance, created = qs.get_or_create(**lookup_kwargs)
        if created:
            log.info(" *** New %r (no:%i) created.", self.class_name, no)
        else:
            log.info(" *** Use existing %r (no:%i) instance.", self.class_name, no)

        for language_code, lang_name in iter_languages(languages=None):
            log.info("Add %r instance values", language_code)
            instance.set_current_language(language_code)
            translation_field_value = self.get_unique_translation_field_value(no, language_code)
            setattr(instance, self.unique_translation_field, translation_field_value)
            self.add_instance_values(instance, language_code, lang_name, no)

        log.info("Save no.%i: %r", no, instance)
        instance.save()
        if self.publisher_model:
            log.info("Publish no.%i: %r", no, instance)
            instance.publish()
