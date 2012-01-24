# coding: utf-8

"""
    Dynamic SITE ID unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin
from django_tools.dynamic_site.models import SiteAlias

class SiteAliasAdmin(admin.ModelAdmin):
    pass # TODO: Make it nice ;)

admin.site.register(SiteAlias, SiteAliasAdmin)
