# coding: utf-8

from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache

class LocalSyncCacheMiddleware(object):
    def process_request(self, request):
        for cache in LocalSyncCache.CACHES:
            cache.check_state()

