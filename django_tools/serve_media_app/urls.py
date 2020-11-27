from django.urls import path

from django_tools.serve_media_app.views.serve_user_files import UserMediaView


app_name = 'serve_media_app'
urlpatterns = [
    path('<slug:user_token>/<path:path>', UserMediaView.as_view(), name='serve-media'),
]
