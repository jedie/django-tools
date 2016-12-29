# coding: utf-8

"""
    Put this into your settings:
    --------------------------------------------------------------------------
        MIDDLEWARE_CLASSES = (
            ...
            'django_tools.middlewares.TracebackLogMiddleware.TracebackLogMiddleware',
            ...
        )
    --------------------------------------------------------------------------

    :copyleft: 2016 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals

import logging


class TracebackLogMiddleware:

    def process_exception(self, request, exception):
        logging.exception('Exception on url: %s' % request.path)

