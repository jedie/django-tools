"""
    Test Local sync cache
    ~~~~~~~~~~~~~~~~~~~~~

    For more information look into DocString in local_sync_cache.py !

    :copyleft: 2011-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import time
import unittest

from django.core.cache import cache

# https://github.com/jedie/django-tools
from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache
from django_tools.local_sync_cache.LocalSyncCacheMiddleware import LocalSyncCacheMiddleware
from django_tools.unittest_utils.assertments import assert_in_logs, assert_pformat_equal


class LocalSyncCacheTest(unittest.TestCase):
    maxDiff = 4000

    def setUp(self):
        LocalSyncCache.CACHES = []
        LocalSyncCache.INIT_COUNTER = {}
        LocalSyncCache._OWN_RESET_TIMES = {}
        cache.clear()

    def testBasic(self):
        c = LocalSyncCache(id="test1")
        c["key1"] = "value1"
        assert_pformat_equal(c, {"key1": "value1"})

        cache.set("test1", time.time())

        c.check_state()
        assert_pformat_equal(c, {})

        cache_information = LocalSyncCache.get_cache_information()
        assert_pformat_equal(len(cache_information), 1)

    def testUniqueID(self):
        LocalSyncCache(id="test1")
        with self.assertLogs(logger="django_tools.local_sync_cache") as logs:
            LocalSyncCache(id="test1")
            assert_in_logs(
                logs,
                line=(
                    "ERROR:django_tools.local_sync_cache:"
                    "ID 'test1' was already used! It must be unique! (Existing ids are: ['test1'])"
                )
            )

    def testEmptyPformatCacheInfo(self):
        txt = LocalSyncCache.pformat_cache_information()
        assert_pformat_equal(txt, "")

    def testPformatCacheInfo(self):
        LocalSyncCache(id="FooBar")
        txt = LocalSyncCache.pformat_cache_information()
        self.assertTrue("id: FooBar" in txt)
        self.assertTrue("instance: {}" in txt)
        self.assertTrue("cleared: False" in txt)

    def testMulti(self):
        assert_pformat_equal(len(LocalSyncCache.CACHES), 0)
        c1 = LocalSyncCache(id="test1")
        assert_pformat_equal(len(LocalSyncCache.CACHES), 1)
        c2 = LocalSyncCache(id="test1", unique_ids=False)
        assert_pformat_equal(len(LocalSyncCache.CACHES), 2)
        c1["c1"] = "foo"
        c2["c2"] = "bar"
        assert_pformat_equal(c1, {"c1": "foo"})
        assert_pformat_equal(c2, {"c2": "bar"})

        c1.check_state()
        c2.check_state()

        assert_pformat_equal(c1, {"c1": "foo"})
        assert_pformat_equal(c2, {"c2": "bar"})

        c1.clear()
        assert_pformat_equal(c1, {})

        # In a "new request" all the same caches should be cleared
        c2.check_state()
        assert_pformat_equal(c2, {})

        cache_information = LocalSyncCache.get_cache_information()
        assert_pformat_equal(len(cache_information), 2)

    #        for item in cache_information:
    #            print item["instance"].id, item

    def testLocalSyncCacheMiddleware(self):
        middleware = LocalSyncCacheMiddleware()

        c1 = LocalSyncCache(id="testLocalSyncCacheMiddleware1")
        c2 = LocalSyncCache(id="testLocalSyncCacheMiddleware1", unique_ids=False)

        c3 = LocalSyncCache(id="testLocalSyncCacheMiddleware2")

        assert_pformat_equal(len(LocalSyncCache.CACHES), 3)

        c1["c1"] = "foo"
        c2["c2"] = "bar"
        c3["foo"] = "bar"

        middleware.process_request(None)

        assert_pformat_equal(c1, {"c1": "foo"})
        assert_pformat_equal(c2, {"c2": "bar"})
        assert_pformat_equal(c3, {"foo": "bar"})

        c1.clear()
        assert_pformat_equal(c1, {})

        # In a "new request" all the same caches should be cleared
        middleware.process_request(None)
        assert_pformat_equal(c2, {})

        # Other caches should be not affected by clear()
        assert_pformat_equal(c3, {"foo": "bar"})

        c1["c1"] = "foo2"
        c2["c2"] = "bar2"

        middleware.process_request(None)

        assert_pformat_equal(c1, {"c1": "foo2"})
        assert_pformat_equal(c2, {"c2": "bar2"})
        assert_pformat_equal(c3, {"foo": "bar"})

        c2.clear()
        assert_pformat_equal(c2, {})

        # In a "new request" all the same caches should be cleared
        middleware.process_request(None)
        assert_pformat_equal(c1, {})

        #        print LocalSyncCache.pformat_cache_information()
        cache_information = LocalSyncCache.get_cache_information()
        assert_pformat_equal(len(cache_information), 3)
        for item in cache_information:
            instance = item["instance"]
            assert_pformat_equal(instance.request_counter, 4)

            if instance.id == "testLocalSyncCacheMiddleware2":
                assert_pformat_equal(instance.own_clear_counter, 0)
                assert_pformat_equal(instance.ext_clear_counter, 0)
                assert_pformat_equal(instance, {"foo": "bar"})
            else:
                assert_pformat_equal(instance.own_clear_counter, 1)
                assert_pformat_equal(instance.ext_clear_counter, 1)
                assert_pformat_equal(instance, {})
