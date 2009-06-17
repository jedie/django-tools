# -*- coding: utf-8 -*-
"""
    threadlocals middleware
    ~~~~~~~~~~~~~~~~~~~~~~~

    make the request object everywhere available (e.g. in model instance). 

    based on: http://code.djangoproject.com/wiki/CookBookThreadlocalsAndUser
    
    Put this into your settings:   
    --------------------------------------------------------------------------
        MIDDLEWARE_CLASSES = (
            ...
            'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware',
            ...
        )
    --------------------------------------------------------------------------
    
    
    Usage:
    --------------------------------------------------------------------------
    from django_tools.middlewares import ThreadLocal
    request = ThreadLocal.get_current_request()
    --------------------------------------------------------------------------
    

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:$

    :copyleft: 2009 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details."""

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local


_thread_locals = local()

def get_current_request():
    """ returns the request object for this thead """
    return _thread_locals.request


class ThreadLocalMiddleware(object):
    """ Simple middleware that adds the request object in thread local storage."""
    def process_request(self, request):
        _thread_locals.request = request
