# coding: utf-8

import time
import logging

from django.core.cache import cache
from django.utils.log import getLogger
from django.conf import settings


logger = getLogger("local_sync_cache")
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())


class LocalSyncCache(dict):
    CACHES = []

    def __init__(self, id=None):
        if id is None:
            raise AssertionError("LocalSyncCache must take a id as argument.")
        self.id = id
        self.last_reset = time.time()

        global_update_time = cache.get(self.id)
        if not global_update_time:
            cache.set(self.id, self.last_reset)

        self.CACHES.append(self)

    def check_state(self):
        """
        Check if we are out-dated or not.
        Should be called at the start of a request. e.g.: by middleware
        """
        global_update_time = cache.get(self.id)
        if global_update_time and self.last_reset < global_update_time:
            # We have out-dated data -> reset dict
            dict.clear(self)
            self.last_reset = time.time()

    def clear(self):
        """
        Must be called from the process/thread witch change the data
        """
        dict.clear(self)
        self.last_reset = time.time()
        cache.set(self.id, self.last_reset)


