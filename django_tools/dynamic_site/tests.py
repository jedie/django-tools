# coding: utf-8

"""
    Dynamic SITE ID unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest

if __name__ == "__main__":
    # run unittest directly
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "test_settings"

from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils import log

from django_tools.unittest_utils.BrowserDebug import debug_response
from django_tools.dynamic_site.models import SiteAlias
from django_tools.unittest_utils.unittest_base import BaseTestCase


class FakeResponse(object):
    _charset = "utf-8"
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code


class DynamicSiteTest(BaseTestCase, TestCase):
    def setUp(self):
        Site.objects.all().delete()
        self.site1 = Site.objects.create(domain="domain_one.tld", name="site 1")
        self.site2 = Site.objects.create(domain="domain_two.tld", name="site 2")

        self.alias1 = SiteAlias.objects.create(site=self.site1, alias="domain_one_alias_one", regex=False)
        self.alias2 = SiteAlias.objects.create(site=self.site1, alias="domain_one_alias_two", regex=False)
        self.alias3 = SiteAlias.objects.create(site=self.site2, alias="www.domain_one.tld", regex=False)
        self.alias4 = SiteAlias.objects.create(site=self.site2, alias=r"^(.*?\.domain_two\.tld)$", regex=True)

    def test_fallback(self):
        response = self.client.get("/display_site/") # request with 'testserver'
        self.assertEqual(response.content,
            'ID from settings: 1 - id from get_current(): 1'
        )

    def test_no_alias1(self):
        response = self.client.get("/display_site/", HTTP_HOST="domain_one.tld")
        self.assertEqual(response.content,
            'ID from settings: 1 - id from get_current(): 1'
        )

    def test_no_alias2(self):
        response = self.client.get("/display_site/", HTTP_HOST="domain_two.tld")
        self.assertEqual(response.content,
            'ID from settings: 2 - id from get_current(): 2'
        )

    def test_string_alias1(self):
        response = self.client.get("/display_site/", HTTP_HOST="domain_one_alias_one")
        self.assertEqual(response.content,
            'ID from settings: 1 - id from get_current(): 1'
        )

    def test_string_alias2(self):
        response = self.client.get("/display_site/", HTTP_HOST="domain_one_alias_two")
        self.assertEqual(response.content,
            'ID from settings: 1 - id from get_current(): 1'
        )

    def test_regex_alias1(self):
        response = self.client.get("/display_site/", HTTP_HOST="foo.domain_two.tld")
        self.assertEqual(response.content,
            'ID from settings: 2 - id from get_current(): 2'
        )

    def test_regex_alias2(self):
        response = self.client.get("/display_site/", HTTP_HOST="foo.bar.domain_two.tld")
        self.assertEqual(response.content,
            'ID from settings: 2 - id from get_current(): 2'
        )

    def test_change(self):
        response = self.client.get("/display_site/", HTTP_HOST="www.domain_one.tld")
        self.assertEqual(response.content,
            'ID from settings: 2 - id from get_current(): 2'
        )

        self.alias3.site = self.site1
        self.alias3.save() # Should clean all site caches

        response = self.client.get("/display_site/", HTTP_HOST="www.domain_one.tld")
        self.assertEqual(response.content,
            'ID from settings: 1 - id from get_current(): 1'
        )

    def test_create(self):
        host = "not_exist_yet.tld"

        # Fallback to default:
        response = self.client.get("/display_site/", HTTP_HOST=host)
        self.assertEqual(response.content,
            'ID from settings: 1 - id from get_current(): 1'
        )

        # Should clean all site caches:
        SiteAlias.objects.create(site=self.site2, alias=host, regex=False)

        response = self.client.get("/display_site/", HTTP_HOST=host)
        self.assertEqual(response.content,
            'ID from settings: 2 - id from get_current(): 2'
        )






if __name__ == "__main__":
    # Run this unittest directly

    # Enable logging to console
    logger1 = log.getLogger("django_tools.DynamicSite")
    log.logging.basicConfig(format='%(created)f %(message)s')
    logger1.setLevel(log.logging.DEBUG)
    logger2 = log.getLogger("django_tools.local_sync_cache")
    logger2.setLevel(log.logging.DEBUG)

    from django.core import management
    management.call_command('test', 'dynamic_site')
