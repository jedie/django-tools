# coding: utf-8

"""
    Dynamic SITE ID unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012-2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin

from django_tools_test_project.django_tools_test_app.views import (
    TemplateDoesNotExists, create_message_normal_response, create_message_redirect_response, display_site,
    get_current_get_parameters, raise_exception, delay_view
)

admin.autodiscover()


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^display_site/$', display_site),
    url(r'^get_current_get_parameters/$', get_current_get_parameters),
    url(r'^raise_exception/(?P<msg>.*?)/$', raise_exception),
    url(r'^raise_template_not_exists/$', TemplateDoesNotExists.as_view()),

    url(r'^create_message_normal_response/(?P<msg>.*?)/$', create_message_normal_response),
    url(r'^create_message_redirect_response/(?P<msg>.*?)/$', create_message_redirect_response),

    url(r'^delay/$', delay_view),
]

if settings.DEBUG:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
