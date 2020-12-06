from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin
from django.urls import path

from django_tools_test_project.django_tools_test_app.views import (
    TemplateDoesNotExists,
    create_message_normal_response,
    create_message_redirect_response,
    delay_view,
    display_site,
    get_current_get_parameters,
    raise_exception,
)


admin.autodiscover()


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^display_site/$', display_site),
    url(r'^get_current_get_parameters/$', get_current_get_parameters),
    url(r'^raise_exception/(?P<msg>.*?)/$', raise_exception),
    url(r'^raise_template_not_exists/$', TemplateDoesNotExists.as_view()),

    url(r'^create_message_normal_response/(?P<msg>.*?)/$', create_message_normal_response),
    url(r'^create_message_redirect_response/(?P<msg>.*?)/$', create_message_redirect_response),

    url(r'^delay/$', delay_view),

    # Serve user files only for authorized users:
    path(settings.MEDIA_URL.lstrip('/'), include('django_tools.serve_media_app.urls')),
]


if settings.DEBUG:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
