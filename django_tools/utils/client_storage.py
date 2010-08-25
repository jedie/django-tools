# coding:utf-8

"""
    Client storage
    ~~~~~~~~~~~~~~
    
    Store data in a client cookie with a security hash.
    
    Usage e.g.:
    --------------------------------------------------------------------------
    from django_tools.utils.client_storage import ClientCookieStorage
    
    def view1(request):
        response = HttpResponse("Hello World!")
        c = ClientCookieStorage(cookie_key="my_key")
        response = c.save_data(my_data_string, response)
        return response
    
    def view2(request):
        c = ClientCookieStorage(cookie_key="my_key")
        data = c.get_data(request)
        if data is not None:
           ...do something...
    --------------------------------------------------------------------------
    
    :copyleft: 2010 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

from django.conf import settings
from django.utils.hashcompat import sha_constructor
from django.middleware import csrf


SALT_LEN = 5 # length of the random salt value
HASH_LEN = 40 # length of a SHA-1 hexdigest


def get_new_salt():
    """
    >>> len(get_new_salt()) == SALT_LEN
    True
    """
    return csrf._get_new_csrf_key()[:SALT_LEN]


class InvalidCookieData(Exception):
    pass

class ClientCookieStorage(object):
    """
    >>> sha_constructor("foo").hexdigest()
    '0beec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33'
    >>> len(sha_constructor("foo").hexdigest()) == HASH_LEN
    True
    >>> c = ClientCookieStorage("foo")
    >>> d = c._append_security_hash("bar")
    >>> c._decode_data(d) == "bar"
    True
    
    >>> c._decode_data("invalid")
    Traceback (most recent call last):
    ...
    InvalidCookieData: Salt/Hash wrong length!
    
    >>> c._decode_data("many invalid data without salt/hash information.")
    Traceback (most recent call last):
    ...
    InvalidCookieData: Salt/Hash inaccurate: invalid literal for int() with base 16: 'y inv'
    
    >>> c._decode_data("invalid123451234567890123456789012345678901234567890")
    Traceback (most recent call last):
    ...
    InvalidCookieData: Hash compare failed!
    """
    def __init__(self, cookie_key):
        self.cookie_key = cookie_key
        
    def _append_security_hash(self, data):
        """ append security hash to the data. """
        salt = get_new_salt()
        hash = sha_constructor(data + salt + settings.SECRET_KEY).hexdigest()
        data += salt + hash
        return data
    
    def _decode_data(self, data):
        """ return the decoded data, but only, if security hash is valid. """
        hash = data[-HASH_LEN:]
        salt = data[-(SALT_LEN+HASH_LEN):-HASH_LEN]
        data = data[:-(SALT_LEN+HASH_LEN)]
        
        if len(salt)!=SALT_LEN or len(hash)!=HASH_LEN:
            raise InvalidCookieData("Salt/Hash wrong length!")
        
        try:
            int(salt, 16)
            int(hash, 16)
        except ValueError, err:
            raise InvalidCookieData("Salt/Hash inaccurate: %s" % err)
        
        hash2 = sha_constructor(data + salt + settings.SECRET_KEY).hexdigest()
        if hash != hash2:
            raise InvalidCookieData("Hash compare failed!")
            
        return data
    
    def save_data(self, data, response, max_age = 60 * 60 * 24 * 7 * 52):
        """ Add a cookie to response object, with data and security hash. """
        data = self._append_security_hash(data)
        response.set_cookie(key=self.cookie_key, value=data, max_age = max_age)
        return response
        
    def get_data(self, request):
        """ Return the stored data from cookie, if security hash is valid. """
        if self.cookie_key not in request.COOKIES:
            return
        
        raw_data = request.COOKIES[self.cookie_key]
        data = self._decode_data(raw_data)
        return data



if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
    print "DocTest end."