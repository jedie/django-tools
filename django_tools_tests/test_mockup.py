# coding: utf-8

"""
    test Mockups
    ~~~~~~~~~~~~
"""


import warnings

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.mockup import ImageDummy
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import TestUserMixin


class TestMockupImage(TestUserMixin, BaseTestCase):
    def test_create_pil_image(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # trigger all warnings

            pil_image = ImageDummy(width=300, height=150).create_pil_image()

            self.assertEqual(pil_image.width, 300)
            self.assertEqual(pil_image.height, 150)

            self.assertEqual(pil_image.verify(), None)

            self.assertEqual(len(w), 0)  # No warnings created

    def test_create_info_image(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # trigger all warnings

            image_dummy = ImageDummy(width=400, height=200)
            self.assertEqual(image_dummy.text_color, "#ffffff")
            self.assertEqual(image_dummy.text_align, "center")
            pil_image = image_dummy.create_info_image(text="foo")

            self.assertEqual(pil_image.width, 400)
            self.assertEqual(pil_image.height, 200)

            self.assertEqual(pil_image.verify(), None)

            self.assertEqual(len(w), 0)  # No warnings created

    def test_create_temp_filer_info_image(self):
        user = self.login(usertype="normal")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # trigger all warnings

            filer_info_image = ImageDummy(width=500, height=300).create_temp_filer_info_image(
                text="A test image", user=user
            )
            self.assertEqual(filer_info_image.width, 500)
            self.assertEqual(filer_info_image.height, 300)

            self.assertEqual(filer_info_image.size, 1791)
            self.assertIn(".png", filer_info_image.path)

            path = filer_info_image.path
            path = path.replace("-", "_")  # e.g.: /django-tools/ -> /django_tools/

            self.assertIn("/django_tools/django_tools_test_project/media/filer_public/", path)

            self.assertEqual(len(w), 0)  # No warnings created
