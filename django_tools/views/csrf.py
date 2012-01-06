# coding:utf-8

"""
    csrf related views
    ~~~~~~~~~~~~~~~~~~

    
    debug_csrf_failure()
    ~~~~~~~~~~~~~~~~~~~~
    Display the normal debug page and not the minimal csrf debug page.
    
    usage: Add this to your settings:
    -----------------------------------------------------------------------    
    CSRF_FAILURE_VIEW='django_tools.views.csrf.debug_csrf_failure'
    -----------------------------------------------------------------------


    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.views.csrf import csrf_failure
from django.conf import settings
from django.http import Http404


class CsrfFailure(Exception):
    pass


def debug_csrf_failure(request, reason=""):
    """
    raised own CsrfFailure() exception to get the normal debug page on
    Csrf failures.
    See also:
        https://docs.djangoproject.com/en/1.3/ref/contrib/csrf/#rejected-requests
        
    More Info: See DocString above.
    """
    if not settings.DEBUG:
        # Use original HttpResponseForbidden:
        return csrf_failure(request, reason)

    raise CsrfFailure("csrf failure debug: %r" % reason)
