# coding: utf-8

"""
    Dynamic SITE ID unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.http import HttpResponse
from django.conf import settings
from django.contrib.sites.models import Site



def display_site(request):

    settings_id = settings.SITE_ID
    current_site = Site.objects.get_current()
    current_id = current_site.id

    txt = "ID from settings: %r - id from get_current(): %r" % (
        settings_id, current_id
    )
    return HttpResponse(txt)



