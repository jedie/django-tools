"""
    test Mockups
    ~~~~~~~~~~~~

    :copyleft: 2018-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import io

from django.conf import settings
from django.core.files import File as DjangoFile

from django_tools.unittest_utils.assertments import assert_endswith, assert_pformat_equal
from django_tools.unittest_utils.mockup import ImageDummy
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import TestUserMixin


class TestMockupImage(TestUserMixin, BaseTestCase):
    def test_create_pil_image(self):
        pil_image = ImageDummy(width=300, height=150).create_pil_image()

        assert_pformat_equal(pil_image.width, 300)
        assert_pformat_equal(pil_image.height, 150)

        assert_pformat_equal(pil_image.verify(), None)

    def test_create_info_image(self):
        image_dummy = ImageDummy(width=400, height=200)
        assert_pformat_equal(image_dummy.text_color, "#ffffff")
        assert_pformat_equal(image_dummy.text_align, "center")
        pil_image = image_dummy.create_info_image(text="foo")

        assert_pformat_equal(pil_image.width, 400)
        assert_pformat_equal(pil_image.height, 200)

        assert_pformat_equal(pil_image.verify(), None)

    def test_create_temp_filer_info_image(self):
        assert_endswith(
            settings.MEDIA_ROOT,
            '/django-tools/.test/media'
        )
        user = self.login(usertype="normal")

        filer_info_image = ImageDummy(
            width=500, height=300, format="png"
        ).create_temp_filer_info_image(
            text="A test image", user=user
        )
        assert_pformat_equal(filer_info_image.width, 500)
        assert_pformat_equal(filer_info_image.height, 300)

        assert_pformat_equal(filer_info_image.size, 1791)
        self.assertIn(".png", filer_info_image.path)

        path = filer_info_image.path
        self.assertIn("/django-tools/.test/media/filer_public/", path)

    def test_create_django_file_info_image(self):
        django_file = ImageDummy(width=100, height=50).create_django_file_info_image(text="foo bar")

        self.assertIsInstance(django_file, DjangoFile)

    def test_in_memory_image_file(self):
        img = ImageDummy(width=1, height=1, format='png').in_memory_image_file(filename='test.png')
        assert isinstance(img, io.BytesIO)
        assert img.name == 'test.png'
        assert img.tell() == 0
        assert img.read().startswith(b'\x89PNG\r\n')
