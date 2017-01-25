# coding: utf-8

from __future__ import unicode_literals

from copy import deepcopy

from django.conf import settings
from django.test import override_settings


TEMPLATE_INVALID_PREFIX='***invalid:'


class set_string_if_invalid(override_settings):
    """
    Decorator that set 'string_if_invalid' in settings.TEMPLATES
    more info in README

    see also:
    https://docs.djangoproject.com/en/1.8/ref/templates/api/#invalid-template-variables
    """
    def __init__(self):
        string_if_invalid='%s%%s***' % TEMPLATE_INVALID_PREFIX

        TEMPLATES = deepcopy(settings.TEMPLATES)
        for template_settings in TEMPLATES:
            template_settings['OPTIONS']['string_if_invalid'] = string_if_invalid

        super(set_string_if_invalid, self).__init__(TEMPLATES=TEMPLATES)
