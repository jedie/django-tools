# coding: utf-8

"""
    need full model and form fields
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2010 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"


from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_tools import validators


class LanguageCodeField(models.CharField):
    """
    >>> LanguageCodeField(max_length=20).run_validators('en-GB')
    
    >>> LanguageCodeField(max_length=20).run_validators("this is wrong")
    Traceback (most recent call last):
        ...
    ValidationError: [u'Enter a valid language code (Accept-Language header format, see RFC2616)']
    """
    default_validators = [validators.validate_language_code]
    description = _("Language Code in Accept-Language header format defined in RFC 2616")


class LanguageCodeFormField(forms.CharField):
    """
    Language Code form field in Accept-Language header format (RFC 2616)
    
    >>> LanguageCodeFormField().clean('en')
    u'en'
    
    >>> LanguageCodeFormField().clean('en-GB')
    u'en-GB'
    
    >>> LanguageCodeFormField().clean("this is wrong")
    Traceback (most recent call last):
        ...
    ValidationError: [u'Enter a valid value.']
    
    >>> LanguageCodeFormField().clean(None)
    Traceback (most recent call last):
        ...
    ValidationError: [u'This field is required.']
    
    >>> LanguageCodeFormField(required=False).clean(None)
    u''
    """
    def __init__(self, *args, **kwargs):
        super(LanguageCodeFormField, self).__init__(*args, **kwargs)
        self.validators.append(validators.validate_language_code)


class SignSeparatedField(forms.CharField):
    """
    >>> SignSeparatedField().clean("one, two")
    (u'one', u'two')
    
    >>> SignSeparatedField().clean("one , two, 3,4")
    (u'one', u'two', u'3', u'4')
    >>> SignSeparatedField(strip_entities=False).clean("one , two, 3,4")
    (u'one ', u' two', u' 3', u'4')
    
    >>> SignSeparatedField(separator=" ").clean("one  two 3")
    (u'one', u'two', u'3')
    >>> SignSeparatedField(separator=" ", skip_empty=False).clean("one  two 3")
    (u'one', u'', u'two', u'3')
    """
    def __init__(self, separator=",", strip_entities=True, skip_empty=True, *args, **kwargs):
        self.separator = separator
        self.strip_entities = strip_entities
        self.skip_empty = skip_empty
        super(SignSeparatedField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(SignSeparatedField, self).clean(value)

        if not value:
            return ""

        if isinstance(value, (list, tuple)):
            return value

        values = []
        for item in value.split(self.separator):
            if self.strip_entities:
                item = item.strip()

            if item in values or self.skip_empty and not item:
                continue

            values.append(item)

        values = tuple(values)
        return values




if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
