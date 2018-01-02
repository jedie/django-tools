# coding: utf-8

"""
    Dynamic SITE ID unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012-2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django_tools_test_project.django_tools_test_app.views import display_site
from django_tools_test_project.django_tools_test_app.views import get_current_get_parameters
from django_tools_test_project.django_tools_test_app.views import raise_exception
from django_tools_test_project.django_tools_test_app.views import create_message_normal_response
from django_tools_test_project.django_tools_test_app.views import create_message_redirect_response
from django_tools_test_project.django_tools_test_app.views import TemplateDoesNotExists
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = (
    url(r'^display_site/$', display_site),
    url(r'^get_current_get_parameters/$', get_current_get_parameters),
    url(r'^raise_exception/(?P<msg>.*?)/$', raise_exception),
    url(r'^raise_template_not_exists/$', TemplateDoesNotExists.as_view()),

    url(r'^create_message_normal_response/(?P<msg>.*?)/$', create_message_normal_response),
    url(r'^create_message_redirect_response/(?P<msg>.*?)/$', create_message_redirect_response),

    url(r'^admin/', include(admin.site.urls)),
)
