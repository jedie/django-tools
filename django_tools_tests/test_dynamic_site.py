# coding: utf-8

"""
    Dynamic SITE ID unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    run only these django_tools_tests:
        .../django-tools $ ./runtests.sh django_tools_tests.test_dynamic_site

    To see debug output: enable LOGGING in:
        .../django-tools/django_tools_test_project/test_settings.py
    
    :copyleft: 2012-2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import unittest

from django.conf import settings
from django.contrib.sites.models import Site
from django.test.utils import override_settings
from django.utils import log
from django.utils.encoding import force_bytes, force_str

from django_tools.unittest_utils.BrowserDebug import debug_response
from django_tools.dynamic_site.models import SiteAlias
from django_tools.unittest_utils.unittest_base import BaseTestCase


class FakeResponse(object):
    _charset = "utf-8"
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code


@override_settings(DEBUG = True)
class DynamicSiteTest(BaseTestCase):
    def setUp(self):
        self.assertTrue(settings.DEBUG, "Must be true to skip hostname validation!")

        Site.objects.all().delete()
        self.site1 = Site.objects.create(pk=1, domain="domain-one.test", name="site 1")
        self.assertEqual(self.site1.pk, 1)
        self.site2 = Site.objects.create(pk=2, domain="domain-two.test", name="site 2")
        self.assertEqual(self.site2.pk, 2)

        self.alias1 = SiteAlias.objects.create(site=self.site1, alias="domain-one-alias-one.test", regex=False)
        self.alias2 = SiteAlias.objects.create(site=self.site1, alias="domain-one-alias-two.test", regex=False)
        self.alias3 = SiteAlias.objects.create(site=self.site2, alias="www.domain-one.test", regex=False)
        self.alias4 = SiteAlias.objects.create(site=self.site2, alias=r"^(.*?\.domain-two\.test)$", regex=True)

    def test_fallback(self):
        response = self.client.get("/display_site/") # request with 'testserver'
        self.assertEqual(response.content.decode("utf-8"),
            'ID from settings: 1 - id from get_current(): 1'
        )

    def test_no_alias1(self):
        response = self.client.get("/display_site/", HTTP_HOST="domain-one.test")
        self.assertEqual(response.content.decode("utf-8"),
            'ID from settings: 1 - id from get_current(): 1'
        )

    def test_no_alias2(self):
        response = self.client.get("/display_site/", HTTP_HOST="domain-two.test")
        self.assertEqual(response.content.decode("utf-8"),
            'ID from settings: 2 - id from get_current(): 2'
        )

    def test_string_alias1(self):
        response = self.client.get("/display_site/", HTTP_HOST="domain-one-alias-one.test")
        self.assertEqual(response.content.decode("utf-8"),
            'ID from settings: 1 - id from get_current(): 1'
        )

    def test_string_alias2(self):
        response = self.client.get("/display_site/", HTTP_HOST="domain-one-alias-two.test")
        self.assertEqual(response.content.decode("utf-8"),
            'ID from settings: 1 - id from get_current(): 1'
        )

    def test_regex_alias1(self):
        response = self.client.get("/display_site/", HTTP_HOST="foo.domain-two.test")
        self.assertEqual(response.content.decode("utf-8"),
            'ID from settings: 2 - id from get_current(): 2'
        )

    def test_regex_alias2(self):
        response = self.client.get("/display_site/", HTTP_HOST="foo.bar.domain-two.test")
        self.assertEqual(response.content.decode("utf-8"),
            'ID from settings: 2 - id from get_current(): 2'
        )

    def test_change(self):
        response = self.client.get("/display_site/", HTTP_HOST="www.domain-one.test")
        self.assertEqual(response.content.decode("utf-8"),
            'ID from settings: 2 - id from get_current(): 2'
        )

        self.alias3.site = self.site1
        self.alias3.save() # Should clean all site caches

        response = self.client.get("/display_site/", HTTP_HOST="www.domain-one.test")
        self.assertEqual(response.content.decode("utf-8"),
            'ID from settings: 1 - id from get_current(): 1'
        )

    def test_create(self):
        host = "does-not-exist-yet.test"

        # Fallback to default:
        response = self.client.get("/display_site/", HTTP_HOST=host)
        self.assertEqual(response.content.decode("utf-8"),
            'ID from settings: 1 - id from get_current(): 1'
        )

        # Should clean all site caches:
        SiteAlias.objects.create(site=self.site2, alias=host, regex=False)

        response = self.client.get("/display_site/", HTTP_HOST=host)
        self.assertEqual(response.content.decode("utf-8"),
            'ID from settings: 2 - id from get_current(): 2'
        )

