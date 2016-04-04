# coding: utf-8

"""
    need full validators
    ~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010-2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function



import os
import re

from django.utils.six.moves import urllib
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, URLValidator
from django.utils.translation import ugettext_lazy as _


# re from django.utils.translation.trans_real.accept_language_re
language_code_re = re.compile(r'^([A-Za-z]{1,8}(?:-[A-Za-z]{1,8})*)$')
validate_language_code = RegexValidator(
    language_code_re,
    _('Enter a valid language code (Accept-Language header format, see RFC2616)'),
    'invalid'
)


class ExistingDirValidator(object):
    def __init__(self, base_path=settings.MEDIA_ROOT):
        self.base_path = os.path.normpath(os.path.abspath(base_path))

    def __call__(self, value):
        abs_path = os.path.normpath(os.path.abspath(os.path.join(self.base_path, value)))

        if not abs_path.startswith(self.base_path):
            if settings.DEBUG:
                msg = _("Directory %r is not in base path ('%s')" % (abs_path, self.base_path))
            else:
                msg = _("Directory is not in base path!")
            raise ValidationError(msg)

        if not os.path.isdir(abs_path):
            if settings.DEBUG:
                msg = _("Directory %r doesn't exist!") % abs_path
            else:
                msg = _("Directory doesn't exist!")

            raise ValidationError(msg)

        return abs_path



class URLValidator2(URLValidator):
    """
    A flexible version of the original django URLValidator ;)
    
    scheme://netloc/path?query#fragment
    """
    regex = re.compile(r'^.+$', re.IGNORECASE)

    def __init__(self, allow_schemes=("http", "https"), allow_all_schemes=False, allow_netloc=True, allow_query=True, allow_fragment=True):
        super(URLValidator2, self).__init__()

        if __debug__ and (allow_schemes or allow_all_schemes) and not allow_netloc:
            raise AssertionError("Can't allow schemes without netloc!")

        if __debug__ and allow_schemes and allow_all_schemes:
            raise Warning("allow_schemes would be ignored, while allow_all_schemes==True!")

        self.allow_schemes = allow_schemes or ()
        self.allow_all_schemes = allow_all_schemes
        self.allow_netloc = allow_netloc
        self.allow_query = allow_query
        self.allow_fragment = allow_fragment

    def __call__(self, value):
        scheme, netloc, path, query, fragment = urllib.parse.urlsplit(value)

        if (scheme or netloc) and not self.allow_schemes and not self.allow_all_schemes and not self.allow_netloc:
            raise ValidationError(_("Please enter a local URL (without protocol/domain)."), code="local")

        if scheme:
            if not self.allow_all_schemes and scheme not in self.allow_schemes:
                raise ValidationError(_("The URL doesn't start with a allowed scheme."), "scheme")

        if netloc and not self.allow_netloc:
            raise ValidationError(_('Enter a valid URL without domain.'), code='netloc')

        if query and not self.allow_query:
            raise ValidationError(_('Enter a valid URL without a query.'), code='query')

        if fragment and not self.allow_fragment:
            raise ValidationError(_('Enter a valid URL without a fragment.'), code='fragment')



if __name__ == "__main__":
    import doctest
    print(doctest.testmod(
#        verbose=True
        verbose=False
    ))
