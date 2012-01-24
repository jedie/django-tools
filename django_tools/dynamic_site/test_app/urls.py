# coding: utf-8

"""
    Dynamic SITE ID unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django_tools.dynamic_site.test_app.views import display_site
from django.conf.urls.defaults import patterns


urlpatterns = patterns('', (r'^display_site/$', display_site))
