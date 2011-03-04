# coding: utf-8

"""
    need full validators
    ~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010-2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import re
import urlparse

if __name__ == "__main__":
    # For doctest only
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

from django.conf import settings
from django.utils.encoding import smart_unicode
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, URLValidator
from django.utils.translation import ugettext_lazy as _


# re from django.utils.translation.trans_real.accept_language_re
language_code_re = re.compile(r'^([A-Za-z]{1,8}(?:-[A-Za-z]{1,8})*)$')
validate_language_code = RegexValidator(
    language_code_re,
    _(u'Enter a valid language code (Accept-Language header format, see RFC2616)'),
    'invalid'
)


class ExistingDirValidator(object):
    """
    >>> settings.DEBUG = False
    
    >>> v = ExistingDirValidator()
    >>> v(settings.MEDIA_ROOT)
    >>> v("does/not/exist")
    Traceback (most recent call last):
        ...
    ValidationError: [u"Directory doesn't exist!"]
    
    >>> v("../")
    Traceback (most recent call last):
        ...
    ValidationError: [u'Directory is not in base path!']
    
    >>> v("//")
    Traceback (most recent call last):
        ...
    ValidationError: [u'Directory is not in base path!']
    
    
    >>> v = ExistingDirValidator("/")
    >>> v("/etc/default/")
    >>> v("var/log")
    """
    def __init__(self, base_path=settings.MEDIA_ROOT):
        self.base_path = os.path.normpath(os.path.abspath(base_path))

    def __call__(self, value):
        value = smart_unicode(value)

        abs_path = os.path.normpath(os.path.abspath(os.path.join(self.base_path, value)))

        if not abs_path.startswith(self.base_path):
            if settings.DEBUG:
                msg = _(u"Directory %r is not in base path ('%s')" % (abs_path, self.base_path))
            else:
                msg = _(u"Directory is not in base path!")
            raise ValidationError(msg)

        if not os.path.isdir(abs_path):
            if settings.DEBUG:
                msg = _(u"Directory %r doesn't exist!") % abs_path
            else:
                msg = _(u"Directory doesn't exist!")

            raise ValidationError(msg)



class URLValidator2(URLValidator):
    """
    A flexible version of the original django URLValidator ;)
    
    scheme://netloc/path?query#fragment
    
       
    >>> URLValidator2(allow_all_schemes=True, allow_netloc=False)
    Traceback (most recent call last):
        ...
    AssertionError: Can't allow schemes without netloc!
    
    
    >>> URLValidator2(allow_schemes=("http","ftp"), allow_all_schemes=True)
    Traceback (most recent call last):
        ...
    Warning: allow_schemes would be ignored, while allow_all_schemes==True!
  
    
    >>> URLValidator2(allow_schemes=("svn",))("svn://domain.tld")
    >>> URLValidator2(allow_schemes=("http","ftp"))("svn://domain.tld")
    Traceback (most recent call last):
        ...
    ValidationError: [u"The URL doesn't start with a allowed scheme."]
    
    
    >>> URLValidator2(allow_query=False)("http://www.domain.tld/without/query/")
    >>> URLValidator2(allow_query=False)("http://www.domain.tld/with/?query")
    Traceback (most recent call last):
        ...
    ValidationError: [u'Enter a valid URL without a query.']
    
    
    >>> URLValidator2(allow_fragment=False)("http://www.domain.tld/without/fragment/")
    >>> URLValidator2(allow_fragment=False)("http://www.domain.tld/with/a/#fragment")
    Traceback (most recent call last):
        ...
    ValidationError: [u'Enter a valid URL without a fragment.']
    
    
    >>> URLValidator2(verify_exists=True)("http://www.pylucid.org/") # Failed if pylucid.org is down ;)
    >>> URLValidator2(verify_exists=True)("http://www.domain.tld/valid/url/does/not/exist/")
    Traceback (most recent call last):
        ...
    ValidationError: [u'This URL appears to be a broken link.']
      
    
    To allow only local path, without protocol/domain do this:
    >>> URLValidator2(allow_schemes=None, allow_netloc=False)("/path/?query#fragment")
    >>> URLValidator2(allow_schemes=None, allow_netloc=False)("www.pylucid.org/path/?query#fragment") # see note below!
    >>> URLValidator2(allow_schemes=None, allow_netloc=False)("http://domain.tld/path/?query#fragment")
    Traceback (most recent call last):
        ...
    ValidationError: [u'Please enter a local URL (without protocol/domain).']
    
    **Note:** Validating the network location (netloc):
    Following the syntax specifications in RFC 1808, urlparse recognizes a
    netloc only if it is properly introduced by ‘//’. Otherwise the input is
    presumed to be a relative URL and thus to start with a path component.
    See: http://docs.python.org/library/urlparse.html#urlparse.urlparse
    
    >>> URLValidator2(allow_schemes=None, allow_netloc=False)("www.pylucid.org/path?query#fragment")
    >>> URLValidator2(allow_schemes=None, allow_netloc=False)("//www.pylucid.org/path?query#fragment")
    Traceback (most recent call last):
        ...
    ValidationError: [u'Please enter a local URL (without protocol/domain).']
    """
    regex = re.compile(r'^.+$', re.IGNORECASE)

    def __init__(self, allow_schemes=("http", "https"), allow_all_schemes=False, allow_netloc=True, allow_query=True, allow_fragment=True,
            verify_exists=False, validator_user_agent=settings.URL_VALIDATOR_USER_AGENT):
        super(URLValidator2, self).__init__()

        if __debug__ and (allow_schemes or allow_all_schemes) and not allow_netloc:
            raise AssertionError("Can't allow schemes without netloc!")

        if __debug__ and allow_schemes and allow_all_schemes:
            raise Warning("allow_schemes would be ignored, while allow_all_schemes==True!")

        self.verify_exists = verify_exists
        self.user_agent = validator_user_agent

        self.allow_schemes = allow_schemes or ()
        self.allow_all_schemes = allow_all_schemes
        self.allow_netloc = allow_netloc
        self.allow_query = allow_query
        self.allow_fragment = allow_fragment

    def __call__(self, value):
        value = smart_unicode(value)
        scheme, netloc, path, query, fragment = urlparse.urlsplit(value)

        if (scheme or netloc) and not self.allow_schemes and not self.allow_all_schemes and not self.allow_netloc:
            raise ValidationError(_(u"Please enter a local URL (without protocol/domain)."), code="local")

        if scheme:
            if not self.allow_all_schemes and scheme not in self.allow_schemes:
                raise ValidationError(_(u"The URL doesn't start with a allowed scheme."), "scheme")

        if netloc and not self.allow_netloc:
            raise ValidationError(_(u'Enter a valid URL without domain.'), code='netloc')

        if query and not self.allow_query:
            raise ValidationError(_(u'Enter a valid URL without a query.'), code='query')

        if fragment and not self.allow_fragment:
            raise ValidationError(_(u'Enter a valid URL without a fragment.'), code='fragment')

        if self.verify_exists:
            super(URLValidator2, self).__call__(value)



if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
