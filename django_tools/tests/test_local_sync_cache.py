# coding: utf-8

"""
    Test Local sync cache
    ~~~~~~~~~~~~~~~~~~~~~
    
    For more information look into DocString in local_sync_cache.py !
    
    :copyleft: 2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest
import time
import pprint

if __name__ == "__main__":
    # run unittest directly
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django_tools.tests.test_settings"

from django.core import management
from django.core.cache import cache

from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache
from django_tools.local_sync_cache.LocalSyncCacheMiddleware import LocalSyncCacheMiddleware


class LocalSyncCacheTest(unittest.TestCase):
    def setUp(self):
        LocalSyncCache.CACHES = []
        LocalSyncCache.INIT_COUNTER = {}
        LocalSyncCache._OWN_RESET_TIMES = {}
        cache.clear()

    def testBasic(self):
        c = LocalSyncCache(id="test1")
        c["key1"] = "value1"
        self.assertEqual(c, {'key1': 'value1'})

        cache.set("test1", time.time())

        c.check_state()
        self.assertEqual(c, {})

        cache_information = LocalSyncCache.get_cache_information()
        self.assertEqual(len(cache_information), 1)

    def testUniqueID(self):
        c1 = LocalSyncCache(id="test1")
        self.assertRaises(AssertionError, LocalSyncCache, id="test1")

    def testEmptyPformatCacheInfo(self):
        txt = LocalSyncCache.pformat_cache_information()
        self.assertEqual(txt, "")

    def testPformatCacheInfo(self):
        LocalSyncCache(id="FooBar")
        txt = LocalSyncCache.pformat_cache_information()
        self.assertTrue("id: FooBar" in txt)
        self.assertTrue("instance: {}" in txt)
        self.assertTrue("cleared: False" in txt)

    def testMulti(self):
        self.assertEqual(len(LocalSyncCache.CACHES), 0)
        c1 = LocalSyncCache(id="test1")
        self.assertEqual(len(LocalSyncCache.CACHES), 1)
        c2 = LocalSyncCache(id="test1", unique_ids=False)
        self.assertEqual(len(LocalSyncCache.CACHES), 2)
        c1["c1"] = "foo"
        c2["c2"] = "bar"
        self.assertEqual(c1, {'c1': 'foo'})
        self.assertEqual(c2, {'c2': 'bar'})

        c1.check_state()
        c2.check_state()

        self.assertEqual(c1, {'c1': 'foo'})
        self.assertEqual(c2, {'c2': 'bar'})

        c1.clear()
        self.assertEqual(c1, {})

        # In a "new request" all the same caches should be cleared
        c2.check_state()
        self.assertEqual(c2, {})

        cache_information = LocalSyncCache.get_cache_information()
        self.assertEqual(len(cache_information), 2)
#        for item in cache_information:
#            print item["instance"].id, item

    def testLocalSyncCacheMiddleware(self):
        middleware = LocalSyncCacheMiddleware()

        c1 = LocalSyncCache(id="testLocalSyncCacheMiddleware1")
        c2 = LocalSyncCache(id="testLocalSyncCacheMiddleware1", unique_ids=False)

        c3 = LocalSyncCache(id="testLocalSyncCacheMiddleware2")

        self.assertEqual(len(LocalSyncCache.CACHES), 3)

        c1["c1"] = "foo"
        c2["c2"] = "bar"
        c3["foo"] = "bar"

        middleware.process_request(None)

        self.assertEqual(c1, {'c1': 'foo'})
        self.assertEqual(c2, {'c2': 'bar'})
        self.assertEqual(c3, {'foo': 'bar'})

        c1.clear()
        self.assertEqual(c1, {})

        # In a "new request" all the same caches should be cleared
        middleware.process_request(None)
        self.assertEqual(c2, {})

        # Other caches should be not affected by clear()
        self.assertEqual(c3, {'foo': 'bar'})

        c1["c1"] = "foo2"
        c2["c2"] = "bar2"

        middleware.process_request(None)

        self.assertEqual(c1, {'c1': 'foo2'})
        self.assertEqual(c2, {'c2': 'bar2'})
        self.assertEqual(c3, {'foo': 'bar'})

        c2.clear()
        self.assertEqual(c2, {})

        # In a "new request" all the same caches should be cleared
        middleware.process_request(None)
        self.assertEqual(c1, {})

#        print LocalSyncCache.pformat_cache_information()
        cache_information = LocalSyncCache.get_cache_information()
        self.assertEqual(len(cache_information), 3)
        for item in cache_information:
            instance = item["instance"]
            self.assertEqual(instance.request_counter, 4)

            if instance.id == "testLocalSyncCacheMiddleware2":
                self.assertEqual(instance.own_clear_counter, 0)
                self.assertEqual(instance.ext_clear_counter, 0)
                self.assertEqual(instance, {'foo': 'bar'})
            else:
                self.assertEqual(instance.own_clear_counter, 1)
                self.assertEqual(instance.ext_clear_counter, 1)
                self.assertEqual(instance, {})


if __name__ == "__main__":
    # Run this unitest directly
#    management.call_command('test', "django_tools.tests.test_local_sync_cache.LocalSyncCacheTest",
#        verbosity=2,
#        failfast=True
#    )
    unittest.main()

