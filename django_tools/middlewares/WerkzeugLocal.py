# -*- coding: utf-8 -*-


"""
    Depend on werkzeug: https://github.com/pallets/werkzeug

    werkzeuglocal middleware
    ~~~~~~~~~~~~~~~~~~~~~~~

    make the request object everywhere available (e.g. in model instance).
    ref https://werkzeug.palletsprojects.com/en/0.15.x/local/

    Put this into your settings:
    --------------------------------------------------------------------------
        MIDDLEWARE_CLASSES = (
            ...
            'django_tools.middlewares.WerkzeugLocal.WerkzeugLocalMiddleware',
            ...
        )
    --------------------------------------------------------------------------


    Usage:
    --------------------------------------------------------------------------
    from django_tools.middlewares.WerkzeugLocal import current_request
    from django_tools.middlewares.WerkzeugLocal import current_user


    --------------------------------------------------------------------------

    :copyleft: 2009-2017 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

from functools import partial

from werkzeug.local import LocalStack, LocalProxy

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object  # fallback for Django < 1.10


def _lookup_object(name):
    return getattr(_request_stack.top, name, None)


_request_stack = LocalStack()
current_request = LocalProxy(partial(_lookup_object, 'request'))
current_user = LocalProxy(partial(_lookup_object, 'user'))


class _RequestContext(object):

    def __init__(self, request):
        self.request = request
        self.user = request.user


class WerkzeugLocalMiddleware(MiddlewareMixin):
    """ Simple middleware that adds the request object in werkzeug local storage."""

    def process_request(self, request):
        _request_stack.push(_RequestContext(request))

    def process_response(self, request, response):
        _request_stack.pop()
        return response

    def process_exception(self, request, exception):
        _request_stack.pop()
