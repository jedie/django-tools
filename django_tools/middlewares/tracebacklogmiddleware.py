"""
Put this into your settings:
--------------------------------------------------------------------------
    MIDDLEWARE_CLASSES = (
        ...
        'django_tools.middlewares.tracebacklogmiddleware.TracebackLogMiddleware',
        ...
    )
--------------------------------------------------------------------------

:copyleft: 2016 by the django-tools team, see AUTHORS for more details.
:license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging


class TracebackLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logging.exception('Exception on url: %s', request.path)  # noqa: LOG015
