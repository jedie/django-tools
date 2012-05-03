# coding:utf-8

"""
    Client storage
    ~~~~~~~~~~~~~~
    
    Use dumps() and loads() from django.core.signing to store data into a Cookie.
    
    See:
    https://docs.djangoproject.com/en/1.4/topics/signing/#verifying-timestamped-values
    
    Usage e.g.:
    --------------------------------------------------------------------------
    from django_tools.utils.client_storage import ClientCookieStorageError, ClientCookieStorage
    
    def view1(request):
        response = HttpResponse("Hello World!")
        c = ClientCookieStorage(cookie_key="my_key", max_age=60)
        response = c.save_data(my_data, response)
        return response
    
    def view2(request):
        c = ClientCookieStorage(cookie_key="my_key", max_age=60)
        try:
            data = c.get_data(request)
        except ClientCookieStorageError, err:
            ...cookie missing or outdated or wrong data...
        else:
           ...do something with the data...
    --------------------------------------------------------------------------
    
    :copyleft: 2010-2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

from django.core import signing


class ClientCookieStorageError(signing.BadSignature):
    pass


class ClientCookieStorage(object):
    """  
    >>> from django.http import HttpResponse, SimpleCookie, HttpRequest
    >>> response = HttpResponse("example")
    >>> c = ClientCookieStorage("foo", max_age=123)
    >>> response = c.save_data("bar", response)
    >>> cookie = response.cookies["foo"]
    >>> cookie_value = cookie.value
    >>> "bar" not in cookie_value
    True
    >>> "foo" not in cookie_value
    True
    >>> cookie["max-age"]
    123
    >>> from django.test.client import RequestFactory
    >>> request = RequestFactory().get('/', HTTP_COOKIE="foo=%s" % cookie_value)
    >>> c = ClientCookieStorage("foo", max_age=123)
    >>> c.get_data(request)
    u'bar'

    >>> c = ClientCookieStorage("wrong name")
    >>> c.get_data(request)
    Traceback (most recent call last):
    ...
    ClientCookieStorageError: Cookie 'wrong name' doesn't exists

    >>> request = RequestFactory().get('/', HTTP_COOKIE="foo=value:timestamp:wrong_dataABCDEFGHIJKLMNOPQ")
    >>> c = ClientCookieStorage("foo")
    >>> c.get_data(request)
    Traceback (most recent call last):
    ...
    ClientCookieStorageError: Can't load data: Signature "wrong_dataABCDEFGHIJKLMNOPQ" does not match
    """
    def __init__(self, cookie_key, max_age=60 * 60 * 24 * 7 * 52, compress=False):
        self.cookie_key = cookie_key
        self.max_age = max_age
        self.compress = compress

    def save_data(self, data, response, **kwargs):
        """ Add a cookie to response object, with data and security hash. """
        signed_data = signing.dumps(data, compress=self.compress, **kwargs)
        response.set_cookie(key=self.cookie_key, value=signed_data, max_age=self.max_age)
        return response

    def get_data(self, request):
        """ Return the stored data from cookie, if security hash is valid. """
        try:
            raw_data = request.COOKIES[self.cookie_key]
        except KeyError:
            raise ClientCookieStorageError("Cookie %r doesn't exists" % self.cookie_key)

        try:
            data = signing.loads(raw_data, max_age=self.max_age)
        except Exception, err:
            raise ClientCookieStorageError("Can't load data: %s" % err)

        return data



if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
    print "DocTest end."
