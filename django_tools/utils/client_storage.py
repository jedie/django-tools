# coding:utf-8

"""
    Client storage
    ~~~~~~~~~~~~~~
    
    Use dumps() and loads() from django.core.signing to store data into a Cookie.
    
    See:
    https://docs.djangoproject.com/en/1.4/topics/signing/#verifying-timestamped-values
    
    Usage e.g.:
    --------------------------------------------------------------------------
    from django_tools.utils.client_storage import SignedCookieStorageError, SignedCookieStorage
    
    def view1(request):
        response = HttpResponse("Hello World!")
        c = SignedCookieStorage(cookie_key="my_key", max_age=60)
        response = c.save_data(my_data, response)
        return response
    
    def view2(request):
        c = SignedCookieStorage(cookie_key="my_key", max_age=60)
        try:
            data = c.get_data(request)
        except SignedCookieStorageError, err:
            ...cookie missing or outdated or wrong data...
        else:
           ...do something with the data...
    --------------------------------------------------------------------------
    
    :copyleft: 2010-2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import os
import warnings

from django.core import signing


class SignedCookieStorageError(signing.BadSignature):
    pass


class SignedCookieStorage(object):
    """  
    see:
        django_tools_tests.test_signed_cookie.TestSignedCookieStorage
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
            raise SignedCookieStorageError("Cookie %r doesn't exists" % self.cookie_key)

        try:
            data = signing.loads(raw_data, max_age=self.max_age)
        except Exception as err:
            raise SignedCookieStorageError("Can't load data: %s" % err)

        return data



class ClientCookieStorage(object):
    """
    Support the old API

    TODO: remove in future
    """
    def __new__(self, *args, **kwargs):
        warnings.warn(
            "ClientCookieStorage is old API! Please change to SignedCookieStorage! This will be removed in the future!",
            FutureWarning,
            stacklevel=2
        )
        return SignedCookieStorage(*args, **kwargs)

