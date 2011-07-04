# coding: utf-8

import unittest
import time

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
        cache.clear()

    def testBasic(self):
        c = LocalSyncCache(id="test1")
        c["key1"] = "value1"
        self.assertEqual(c, {'key1': 'value1'})

        cache.set("test1", time.time())

        c.check_state()
        self.assertEqual(c, {})

    def testMulti(self):
        self.assertEqual(len(LocalSyncCache.CACHES), 0)
        c1 = LocalSyncCache(id="test1")
        self.assertEqual(len(LocalSyncCache.CACHES), 1)
        c2 = LocalSyncCache(id="test1")
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

        # "new request"
        c2.check_state()
        self.assertEqual(c2, {})

    def testLocalSyncCacheMiddleware(self):
        middleware = LocalSyncCacheMiddleware()

        c1 = LocalSyncCache(id="test1")
        c2 = LocalSyncCache(id="test1")
        self.assertEqual(len(LocalSyncCache.CACHES), 2)

        c1["c1"] = "foo"
        c2["c2"] = "bar"

        middleware.process_request(None)

        self.assertEqual(c1, {'c1': 'foo'})
        self.assertEqual(c2, {'c2': 'bar'})

        c1.clear()
        self.assertEqual(c1, {})

        # "new request"
        middleware.process_request(None)
        self.assertEqual(c2, {})




if __name__ == "__main__":
    # Run this unitest directly
#    management.call_command('test', "django_tools.tests.test_local_sync_cache.LocalSyncCacheTest",
#        verbosity=2,
#        failfast=True
#    )
    unittest.main()

