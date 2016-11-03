# coding: utf-8

"""
    test Mockups
    ~~~~~~~~~~~~
"""

from __future__ import unicode_literals, print_function

import unittest

from django_tools.unittest_utils.mockup import create_pil_image, create_info_image
from django_tools.unittest_utils.unittest_base import BaseTestCase


#==============================================================================
# TODO: Remove after django-filer v1.2.6 is released!
# Problem: AttributeError: 'Manager' object has no attribute '_inherited'
# with Django v1.10 and django-filer v1.2.5
# see also:
# https://github.com/divio/django-filer/issues/899

from pip._vendor.packaging.version import parse as _parse_version
from filer import __version__ as _filer_version
from django import __version__ as _django_version

_filer_version=_parse_version(_filer_version)
_django_version=_parse_version(_django_version)

if _django_version < _parse_version("1.10") or _filer_version >= _parse_version("1.2.6"):
    SKIP_TEST = False
    from django_tools.unittest_utils.mockup import create_temp_filer_info_image
else:
    SKIP_TEST = True

#==============================================================================


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

    @unittest.skipIf(SKIP_TEST, "Combination Django v1.10 and django-filer v1.2.5")
    def test_create_temp_filer_info_image(self):
        self.create_testusers(verbosity=1)

        user = self.login(usertype="normal")

        filer_info_image = create_temp_filer_info_image(width=500, height=300, text="A test image", user=user)
        self.assertEqual(filer_info_image.width, 500)
        self.assertEqual(filer_info_image.height, 300)

        self.assertEqual(filer_info_image.size, 1791)
        self.assertIn("django-tools/filer_public/", filer_info_image.path)
        self.assertIn(".png", filer_info_image.path)
