from django.conf import settings
from django.conf.urls import static
from django.contrib import admin
from django.urls import include, path

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
    path('admin/', admin.site.urls),

    path('display_site/', display_site),
    path('get_current_get_parameters/', get_current_get_parameters),
    path('raise_exception/<str:msg>/', raise_exception),
    path('raise_template_not_exists/', TemplateDoesNotExists.as_view()),

    path('create_message_normal_response/<str:msg>/', create_message_normal_response),
    path('create_message_redirect_response/<str:msg>/', create_message_redirect_response),

    path('delay/', delay_view),

    # Serve user files only for authorized users:
    path(settings.MEDIA_URL.lstrip('/'), include('django_tools.serve_media_app.urls')),
]


if settings.DEBUG:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
