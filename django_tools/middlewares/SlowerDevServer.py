"""
    SlowerDevServer
    ~~~~~~~~~~~~~~~

    Simple slow down the django developer server.
    The middleware insert in every 200 response a time.sleep

    Put this into your settings:
    --------------------------------------------------------------------------
        MIDDLEWARE_CLASSES = (
            ...
            'django_tools.middlewares.SlowerDevServer.SlowerDevServerMiddleware',
            ...
        )
        SLOWER_DEV_SERVER_SLEEP = 0.3 # time.sleep() value (in sec.)
    --------------------------------------------------------------------------

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:$

    :copyleft: 2009 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import time
import warnings

from django.conf import settings


try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object  # fallback for Django < 1.10


class SlowerDevServerMiddleware(MiddlewareMixin):
    def __init__(self):
        warnings.warn("Slower developer server used!", stacklevel=2)

    def process_response(self, request, response):
        if response.status_code == 200:
            print(f"SlowerDevServerMiddleware: Wait for {settings.SLOWER_DEV_SERVER_SLEEP}Sec...")
            time.sleep(settings.SLOWER_DEV_SERVER_SLEEP)
        return response
