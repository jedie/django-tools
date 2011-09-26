# coding: utf-8

"""
    need full model and form fields
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010-2011 by the django-tools team, see AUTHORS for more details.
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


class LanguageCodeModelField(models.CharField):
    """
    >>> LanguageCodeModelField(max_length=20).run_validators('en-GB')
    
    >>> LanguageCodeModelField(max_length=20).run_validators("this is wrong")
    Traceback (most recent call last):
        ...
    ValidationError: [u'Enter a valid language code (Accept-Language header format, see RFC2616)']
    """
    default_validators = [validators.validate_language_code]
    description = _("Language Code in Accept-Language header format defined in RFC 2616")

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^django_tools\.fields\.language_code\.LanguageCodeModelField"])
except ImportError:
    pass

#------------------------------------------------------------------------------


if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
