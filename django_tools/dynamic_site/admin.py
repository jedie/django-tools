# coding: utf-8

"""
    Dynamic SITE ID - model admin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings

from django.contrib import admin
from django_tools.dynamic_site.models import SiteAlias


class SiteAliasAdmin(admin.ModelAdmin):
    list_display = (
        "id", "site", "alias", "regex"
    )
    list_display_links = ("id", "alias")
    list_filter = ("site", "regex")
    search_fields = ("alias",)


if getattr(settings, "USE_DYNAMIC_SITE_MIDDLEWARE", False) == True:
    admin.site.register(SiteAlias, SiteAliasAdmin)
