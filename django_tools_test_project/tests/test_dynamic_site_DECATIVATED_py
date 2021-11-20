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

import logging
import unittest

from django.conf import settings
from django.contrib.sites.models import Site
from django.test.utils import override_settings
from django.utils import log

# https://github.com/jedie/django-tools
from django_tools.dynamic_site.models import SiteAlias
from django_tools.unittest_utils.BrowserDebug import debug_response
from django_tools.unittest_utils.unittest_base import BaseTestCase

log = logging.getLogger(__name__)


class FakeResponse(object):
    _charset = "utf-8"
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code

@override_settings(DEBUG = True)
class DynamicSiteTest(BaseTestCase):
    def setUp(self):
        self.assertTrue(settings.DEBUG, "Must be true to skip hostname validation!")

        self.assertEqual(Site.objects.all().count(), 1)
        Site.objects.all().delete()
        self.site1 = Site.objects.create(pk=1, domain="domain-one.test", name="site 1")
        self.assertEqual(self.site1.pk, 1)
        self.site2 = Site.objects.create(pk=2, domain="domain-two.test", name="site 2")
        self.assertEqual(self.site2.pk, 2)

        self.assertEqual(SiteAlias.objects.all().count(), 0)
        self.alias1 = SiteAlias.objects.create(site=self.site1, alias="domain-one-alias-one.test", regex=False)
        self.alias2 = SiteAlias.objects.create(site=self.site1, alias="domain-one-alias-two.test", regex=False)
        self.alias3 = SiteAlias.objects.create(site=self.site2, alias="www.alias-two.test", regex=False)
        self.alias4 = SiteAlias.objects.create(site=self.site2, alias=r"^(.*?\.domain-two\.test)$", regex=True)

        SiteAlias.objects.clear_cache()

    def tearDown(self):
        Site.objects.all().delete()
        SiteAlias.objects.all().delete()

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
        self.assertEqual(
            SiteAlias.objects.get(alias="www.alias-two.test").site.id, 2
        )
        response = self.client.get("/display_site/", HTTP_HOST="www.alias-two.test")
        self.assertEqual(response.content.decode("utf-8"),
            'ID from settings: 2 - id from get_current(): 2'
        )

        self.assertEqual(self.alias3.alias, "www.alias-two.test")
        self.alias3.site = self.site1 # change destination from site ID 1 to site ID 2
        self.alias3.save() # Should clean all site caches, so hat ID 2 ist used:

        self.assertEqual(
            SiteAlias.objects.get(alias="www.alias-two.test").site.id, 1
        )

        response = self.client.get("/display_site/", HTTP_HOST="www.alias-two.test")
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

        # Create a alias from "does-not-exist-yet.test" -> site 2
        site_alias = SiteAlias.objects.create(site=self.site2, alias=host, regex=False)

        self.assertEqual(SiteAlias.objects.get(alias=host).site.pk, 2)

        # Creation should clean the cache, so that site1 will not be used:

        response = self.client.get("/display_site/", HTTP_HOST=host)
        self.assertEqual(response.content.decode("utf-8"),
            'ID from settings: 2 - id from get_current(): 2'
        )
