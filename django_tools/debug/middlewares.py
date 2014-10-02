# coding: utf-8

"""
    debug middlewares
    ~~~~~~~~~~~~~~~~~
    
    more information in the README.
    
    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


from django.conf import settings

class SetRequestDebugMiddleware(object):
    """
    add 'debug' bool attribute to request object
    
    debug is on if:
        settings.DEBUG == True
    *OR*
        remote IP is in settings.INTERNAL_IPS
    """
    def process_request(self, request):
        request.debug = settings.DEBUG or request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS
