# coding: utf-8

"""
    need full model and form fields
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010-2016 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_tools import validators


class LanguageCodeFormField(forms.CharField):
    """
    Language Code form field in Accept-Language header format (RFC 2616)

    >>> LanguageCodeFormField().clean('en')
    'en'

    >>> LanguageCodeFormField().clean('en-GB')
    'en-GB'

    >>> try:
    ...     LanguageCodeFormField().clean("this is wrong")
    ... except Exception as err:
    ...     print(err.__class__.__name__, err)
    ValidationError ['Enter a valid language code (Accept-Language header format, see RFC2616)']

    >>> try:
    ...     LanguageCodeFormField().clean(None)
    ... except Exception as err:
    ...     print(err.__class__.__name__, err)
    ValidationError ['This field is required.']

    >>> LanguageCodeFormField(required=False).clean(None)
    ''
    """
    def __init__(self, *args, **kwargs):
        super(LanguageCodeFormField, self).__init__(*args, **kwargs)
        self.validators.append(validators.validate_language_code)


class LanguageCodeModelField(models.CharField):
    """
    >>> LanguageCodeModelField(max_length=20).run_validators('en-GB')

    >>> try:
    ...     LanguageCodeModelField(max_length=20).run_validators("this is wrong")
    ... except Exception as err:
    ...     print(err.__class__.__name__, err)
    ValidationError ['Enter a valid language code (Accept-Language header format, see RFC2616)']
    """
    default_validators = [validators.validate_language_code]
    description = _("Language Code in Accept-Language header format defined in RFC 2616")
