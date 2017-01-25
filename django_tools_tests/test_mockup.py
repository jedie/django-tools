# coding: utf-8

"""
    test Mockups
    ~~~~~~~~~~~~
"""

from __future__ import unicode_literals, print_function, absolute_import

import django

from django_tools.unittest_utils.mockup import create_pil_image, create_info_image, \
    create_temp_filer_info_image
from django_tools.unittest_utils.unittest_base import BaseTestCase


class TestMockup(BaseTestCase):
    def test_create_pil_image(self):
        pil_image = create_pil_image(width=300, height=150)

        self.assertEqual(pil_image.width, 300)
        self.assertEqual(pil_image.height, 150)

        self.assertEqual(pil_image.verify(), None)

    def test_create_info_image(self):
        pil_image = create_info_image(width=400, height=200, text="foo", fill='#ffffff', align='center')

        self.assertEqual(pil_image.width, 400)
        self.assertEqual(pil_image.height, 200)

        self.assertEqual(pil_image.verify(), None)

    def test_create_temp_filer_info_image(self):
        self.create_testusers(verbosity=1)

        user = self.login(usertype="normal")

        filer_info_image = create_temp_filer_info_image(width=500, height=300, text="A test image", user=user)
        self.assertEqual(filer_info_image.width, 500)
        self.assertEqual(filer_info_image.height, 300)

        self.assertEqual(filer_info_image.size, 1791)
        self.assertIn(".png", filer_info_image.path)

        if django.VERSION < (1, 10):
            self.assertIn("django-tools/filer_public/", filer_info_image.path)
            #--------------------^
        else:
            self.assertIn("django_tools/filer_public/", filer_info_image.path)
            #--------------------^
