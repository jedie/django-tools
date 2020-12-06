import io
import logging
import tempfile
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.storage import DefaultStorage
from django.http import FileResponse
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from model_bakery import baker

from django_tools.serve_media_app.exceptions import NoUserToken
from django_tools.serve_media_app.models import UserMediaTokenModel, generate_media_path
from django_tools.unittest_utils.mockup import ImageDummy
from django_tools_test_project.django_tools_test_app.models import UserMediaFiles


class UserMediaViewsTestCase(TestCase):
    def test_generate_media_path(self):
        with mock.patch('secrets.token_urlsafe', return_value='ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            user = baker.make(User, username='owner')

        with mock.patch('secrets.token_urlsafe', return_value='12345678901234567890'):
            media_path = generate_media_path(user=user, filename='Foo Bar!.ext')
            assert media_path == 'abcdefghijkl/12345678901234567890/foo_bar.ext'

        # Test whats happen, if token was deleted
        UserMediaTokenModel.objects.all().delete()
        with self.assertLogs(logger='django_tools', level=logging.ERROR) as log:
            with self.assertRaises(NoUserToken):
                generate_media_path(user=user, filename='Foo Bar!.ext')
        assert log.output == [
            'ERROR:django_tools.serve_media_app.exceptions:Current user "owner" has no token!'
        ]

    def test_basic(self):
        assert settings.MEDIA_URL == '/media/'
        assert get_user_model() == User

        url = reverse('serve_media_app:serve-media', kwargs={'user_token': 'foo', 'path': 'bar'})
        assert url == '/media/foo/bar'

        with tempfile.TemporaryDirectory() as temp:
            with override_settings(MEDIA_ROOT=temp):
                user = baker.make(User, username='owner')
                file_path = generate_media_path(user, filename='foobar.txt')

                storage = DefaultStorage()
                content = io.BytesIO('Test äöüß !'.encode())
                final_file_path = storage.save(file_path, content)
                assert final_file_path == file_path

                url = f'/media/{file_path}'

                # Anonymous has no access:
                response = self.client.get(url)
                assert response.status_code == 403

                # Can't access with wrong user:
                other_user = baker.make(User, username='not-owner')
                self.client.force_login(other_user)
                response = self.client.get(url)
                assert response.status_code == 403

                # Can access with the right user:
                self.client.force_login(user)
                response = self.client.get(url)
                assert response.status_code == 200
                assert isinstance(response, FileResponse)
                assert response.getvalue().decode('UTF-8') == 'Test äöüß !'

                # Test whats happen, if token was deleted
                UserMediaTokenModel.objects.all().delete()
                with self.assertLogs(logger='django_tools', level=logging.ERROR) as log:
                    response = self.client.get(url)
                assert response.status_code == 400  # SuspiciousOperation -> HttpResponseBadRequest
                assert log.output == [
                    'ERROR:django_tools.serve_media_app.exceptions:Current user "owner" has no token!'
                ]

    def test_via_model(self):
        with mock.patch('secrets.token_urlsafe', return_value='ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            user = baker.make(User, username='owner')

        other_user = baker.make(User, username='not-owner')

        with tempfile.TemporaryDirectory() as temp:
            with override_settings(MEDIA_ROOT=temp):
                with mock.patch('secrets.token_urlsafe', return_value='12345678901234567890'):
                    instance = UserMediaFiles.objects.create(
                        user=user,
                        file=File(io.BytesIO('Test äöüß !'.encode()), name='filename.ext'),
                        image=ImageDummy(width=1, height=1).create_django_file_info_image(text=None),
                    )

                token_instance = UserMediaTokenModel.objects.get(user=user)
                assert repr(token_instance) == (
                    f"<UserMediaTokenModel: user:{user.pk} token:'abcdefghijkl' ({token_instance.pk})>"
                )

                user_token = UserMediaTokenModel.objects.get_user_token(user)
                assert user_token == 'abcdefghijkl'
                other_user_token = UserMediaTokenModel.objects.get_user_token(other_user)
                assert other_user_token != user_token

                urls = (
                    '/media/abcdefghijkl/12345678901234567890/filename.ext',
                    '/media/abcdefghijkl/12345678901234567890/dummy.jpeg'
                )

                assert instance.file.url == urls[0]
                assert instance.image.url == urls[1]

                # Anonymous has no access:
                for url in urls:
                    response = self.client.get(url)
                    assert response.status_code == 403

                # Can't access with wrong user:
                self.client = Client()
                self.client.force_login(other_user)
                for url in urls:
                    response = self.client.get(url)
                    assert response.status_code == 403

                # Can access with the right user:
                self.client = Client()
                self.client.force_login(user)
                response = self.client.get('/media/abcdefghijkl/12345678901234567890/filename.ext')
                assert response.status_code == 200
                assert isinstance(response, FileResponse)
                assert response.getvalue().decode('UTF-8') == 'Test äöüß !'
                response = self.client.get('/media/abcdefghijkl/12345678901234567890/dummy.jpeg')
                assert response.status_code == 200
                assert isinstance(response, FileResponse)
                assert len(response.getvalue())

                # Test whats happen, if token was deleted
                UserMediaTokenModel.objects.all().delete()
                for url in urls:
                    response = self.client.get(url)
                    assert response.status_code == 400  # SuspiciousOperation -> HttpResponseBadRequest
