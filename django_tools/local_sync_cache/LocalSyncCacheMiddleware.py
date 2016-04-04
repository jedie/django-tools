# coding: utf-8

"""
    Local sync cache Middleware
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Calls check_state() in every existing LocalSyncCache instance.
    
    For more information look into DocString in local_sync_cache.py !
    
    :copyleft: 2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache

class LocalSyncCacheMiddleware(object):
    def process_request(self, request):
        for cache in LocalSyncCache.CACHES:
            cache.check_state()

