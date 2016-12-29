# coding: utf-8

"""
    Dynamic SITE ID unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import json

from django.http import HttpResponse
from django.conf import settings
from django.contrib.sites.models import Site

from django_tools.middlewares.ThreadLocal import get_current_request



def display_site(request):

    settings_id = settings.SITE_ID
    current_site = Site.objects.get_current()
    current_id = current_site.id

    txt = "ID from settings: %r - id from get_current(): %r" % (
        settings_id, current_id
    )
    return HttpResponse(txt)



def raise_exception(request, msg=""):
    """
    This view just raises an exception as a way to test middleware exception
    handling.
    """
    raise Exception(msg)


def get_current_get_parameters(request):
    """
    Returns a JSON version of request.GET from the current request
    """
    return HttpResponse(json.dumps(get_current_request().GET))
