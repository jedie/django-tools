import io
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.files.storage import DefaultStorage
from django.http import FileResponse
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from override_storage import locmem_stats_override_storage

from django_tools.serve_media_app.constants import USER_TOKEN_LENGTH
from django_tools.serve_media_app.models import UserMediaTokenModel, generate_media_path
from django_tools.serve_media_app.views.serve_user_files import serve_file_request
from django_tools.unittest_utils.signals import SignalsContextManager


class SignalsTestCase(TestCase):
    def test_create_user_token_via_signal(self):
        assert UserMediaTokenModel.objects.count() == 0
        UserModel = get_user_model()
        user = baker.make(UserModel)
        assert UserMediaTokenModel.objects.count() == 1

        instance = UserMediaTokenModel.objects.get_from_user(user)
        assert instance is not None
        token1 = instance.token
        assert len(token1) == USER_TOKEN_LENGTH

        user.save()  # Token must be not changed
        user = UserModel.objects.get(pk=user.pk)
        instance = UserMediaTokenModel.objects.get_from_user(user)
        assert instance.token == token1

    @locmem_stats_override_storage()
    def test_serve_file_request_signal(self):
        with mock.patch('secrets.token_urlsafe', return_value='ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            super_user = baker.make(get_user_model(), is_superuser=True, email='super@user.tld')
        self.client.force_login(super_user)

        with mock.patch('secrets.token_urlsafe', return_value='ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            media_path = generate_media_path(user=super_user, filename='foobar.ext')

        assert media_path == 'abcdefghijkl/abcdefghijklmnopqrstuvwx/foobar.ext'
        storage = DefaultStorage()
        content = io.BytesIO('Test äöüß !'.encode())
        storage.save(media_path, content)

        assert settings.MEDIA_URL == '/media/'
        url = reverse(
            'serve_media_app:serve-media',
            kwargs={'user_token': 'abcdefghijkl', 'path': 'abcdefghijklmnopqrstuvwx/foobar.ext'}
        )
        assert url == '/media/abcdefghijkl/abcdefghijklmnopqrstuvwx/foobar.ext'

        # Test with a signal callback that will not allow the access:

        def deny_access_callback(user, path, media_path, **kwargs):
            assert user.email == 'super@user.tld'
            assert path == 'abcdefghijklmnopqrstuvwx/foobar.ext'
            assert media_path == 'abcdefghijkl/abcdefghijklmnopqrstuvwx/foobar.ext'
            raise PermissionDenied

        with SignalsContextManager(serve_file_request, deny_access_callback):
            response = self.client.get(url)
            assert response.status_code == 403

        # Test with a signal callback that allowes the access:

        def allow_access_callback(user, path, media_path, **kwargs):
            assert user.email == 'super@user.tld'
            assert path == 'abcdefghijklmnopqrstuvwx/foobar.ext'
            assert media_path == 'abcdefghijkl/abcdefghijklmnopqrstuvwx/foobar.ext'

        with SignalsContextManager(serve_file_request, allow_access_callback):
            response = self.client.get(url)
            assert response.status_code == 200
            assert isinstance(response, FileResponse)
            assert response.getvalue().decode('UTF-8') == 'Test äöüß !'
