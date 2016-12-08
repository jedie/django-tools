# coding:utf-8


"""
    url form/model field
    ~~~~~~~~~~~~~~~~~~~~

    flexible URL form and model field used own URLValidator2.

    :copyleft: 2011-2016 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


from django.db.models.fields import CharField as OriginModelCharField
from django.forms.fields import CharField as OriginFormsCharField
from django.utils.translation import ugettext_lazy as _

from django_tools.validators import URLValidator2


class URLFormField2(OriginFormsCharField):
    """
    A flexible version of the original django form URLField ;)

    Please read the django_tools.validators.URLValidator2 DocString, too!


    To allow only local domains, disallow scheme and netloc:
    >>> URLFormField2(allow_schemes=None, allow_netloc=False).clean("/path/?query#fragment")
    u'/path/?query#fragment'

    >>> try:
    ...     URLFormField2(allow_schemes=None, allow_netloc=False).clean("http://domain.tld/path/?query#fragment")
    ... except Exception as err:
    ...     print(err.__class__.__name__, err)
    ValidationError ['Please enter a local URL (without protocol/domain).']

    **Note:** this is also a valid "local" path (more info in URLValidator2 DocString):
    >>> URLFormField2(allow_schemes=None, allow_netloc=False).clean("domain.tld/path/?query#fragment")
    u'domain.tld/path/?query#fragment'


    >>> URLFormField2(allow_schemes=("svn",)).clean("svn://domain.tld")
    u'svn://domain.tld'

    >>> try:
    ...     URLFormField2(allow_schemes=("http","ftp")).clean("svn://domain.tld")
    ... except Exception as err:
    ...     print(err.__class__.__name__, err)
    ValidationError ["The URL doesn't start with a allowed scheme."]
    """
    default_error_messages = {
        'invalid': _('Enter a valid URL.'),
        'invalid_link': _('This URL appears to be a broken link.'),
    }

    def __init__(self, max_length=None, min_length=None, verify_exists=False,
            allow_schemes=("http", "https"), allow_all_schemes=False, allow_netloc=True,
            allow_query=True, allow_fragment=True, *args, **kwargs):

        super(URLFormField2, self).__init__(max_length, min_length, *args, **kwargs)

        self.validators.append(
            URLValidator2(
                allow_schemes=allow_schemes, allow_all_schemes=allow_all_schemes, allow_netloc=allow_netloc,
                allow_query=allow_query, allow_fragment=allow_fragment
            )
        )



class URLModelField2(OriginModelCharField):
    """
    A flexible version of the original django model URLField ;)

    Please read the django_tools.validators.URLValidator2 DocString, too!


    >>> f = URLModelField2(verify_exists=False).formfield()
    >>> isinstance(f, URLFormField2)
    True
    >>> f.clean(u"http://www.domain.tld/path?query#fragment")
    u'http://www.domain.tld/path?query#fragment'

    >>> f = URLModelField2().formfield()

    >>> try:
    ...     f.clean("svn://domain.tld")
    ... except Exception as err:
    ...     print(err.__class__.__name__, err)
    ValidationError ["The URL doesn't start with a allowed scheme."]


    >>> f = URLModelField2(allow_query=False).formfield()
    >>> f.clean("http://www.domain.tld/without/query/")
    u'http://www.domain.tld/without/query/'

    >>> try:
    ...     f.clean("http://www.domain.tld/with/?query")
    ... except Exception as err:
    ...     print(err.__class__.__name__, err)
    ValidationError ['Enter a valid URL without a query.']

    """
    description = _("URL")

    def __init__(self, verbose_name=None, name=None, verify_exists=True,
            allow_schemes=("http", "https"), allow_all_schemes=False, allow_netloc=True,
            allow_query=True, allow_fragment=True, **kwargs):

        kwargs['max_length'] = kwargs.get('max_length', 200)
        OriginModelCharField.__init__(self, verbose_name, name, **kwargs)

        self.allow_schemes = allow_schemes or ()
        self.allow_all_schemes = allow_all_schemes
        self.allow_netloc = allow_netloc
        self.allow_query = allow_query
        self.allow_fragment = allow_fragment

        self.validators.append(
            URLValidator2(
                allow_schemes=allow_schemes, allow_all_schemes=allow_all_schemes, allow_netloc=allow_netloc,
                allow_query=allow_query, allow_fragment=allow_fragment
            )
        )

    def formfield(self, **kwargs):
        # As with CharField, this will cause URL validation to be performed twice
        defaults = {
            'form_class': URLFormField2,

            "allow_schemes":self.allow_schemes,
            "allow_all_schemes":self.allow_all_schemes,
            "allow_netloc":self.allow_netloc,
            "allow_query":self.allow_query,
            "allow_fragment":self.allow_fragment,
        }
        defaults.update(kwargs)
        return super(URLModelField2, self).formfield(**defaults)

