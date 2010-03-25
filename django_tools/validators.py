# coding: utf-8

"""
    need full validators
    ~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2010 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import re

from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


# re from django.utils.translation.trans_real.accept_language_re
language_code_re = re.compile(r'^([A-Za-z]{1,8}(?:-[A-Za-z]{1,8})*)$')
validate_language_code = RegexValidator(
    language_code_re,
    _(u'Enter a valid language code (Accept-Language header format, see RFC2616)'),
    'invalid'
)
