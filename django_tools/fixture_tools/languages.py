

import logging

from django.conf import settings
from django.utils import translation


log = logging.getLogger(__name__)


def iter_languages(languages=None):
    """
    Iterate over all existing languages with activated translations.
    """
    if languages is None:
        languages = settings.LANGUAGES

    for language_code, lang_name in languages:
        with translation.override(language_code):
            yield language_code, lang_name
