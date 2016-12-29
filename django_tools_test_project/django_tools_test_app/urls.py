# coding: utf-8

"""
    Dynamic SITE ID unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012-2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


from django_tools_test_project.django_tools_test_app.views import display_site
from django_tools_test_project.django_tools_test_app.views import get_current_get_parameters
from django_tools_test_project.django_tools_test_app.views import raise_exception
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = (
    url(r'^display_site/$', display_site),
    url(r'^get_current_get_parameters/$', get_current_get_parameters),
    url(r'^raise_exception/(?P<msg>.*?)/$', raise_exception),

    url(r'^admin/', include(admin.site.urls)),
)
