# coding: utf-8

"""
    Local sync cache
    ~~~~~~~~~~~~~~~~
    
    The Problem:
    If you use a normal dict for cache some values, you can't clear it in
    a multi-threaded environment, because you have no access to the dict in
    other threads.
    
    The Solution:
    Use LocalSyncCache() as a cache dict. If dict.clear() called, the dict
    in all threads would be cleared.
    
    How it works:
    * Every cache dict memorize his own creation/reset time.  
    * in dict.clear() the reset time would be saved
      into django cache (to share it with all threads)
    * On every request the LocalSyncCacheMiddleware called all existing cache dict
      in the current threads to look into the shared django cache, if they 
      are outdatet or not. If they are outdated, the dict would be cleaned. 
    
    
    usage
    ~~~~~
    
    Add LocalSyncCacheMiddleware to settings, e.g:
    ---------------------------------------------------------------------------
        MIDDLEWARE_CLASSES = (
            ...
            'django_tools.local_sync_cache.LocalSyncCacheMiddleware.LocalSyncCacheMiddleware',
            ...
        )
    ---------------------------------------------------------------------------
    

    Create a cache dict with a id.
    Use it in a model, e.g.:
    ---------------------------------------------------------------------------
        from django.db import models
        from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache
        
        class PageTree(models.Model):
            parent = models.ForeignKey("self", null=True, blank=True)
            slug = models.SlugField()
            
            _url_cache = LocalSyncCache(id="PageTree_absolute_url") # <<<---
            def get_absolute_url(self):
                if self.pk in self._url_cache:
                    return self._url_cache[self.pk]
        
                if self.parent:
                    parent_url = self.parent.get_absolute_url()
                    url = parent_url + self.slug + "/"
                else:
                    url = "/" + self.slug + "/"
        
                self._url_cache[self.pk] = url
                return url
                
        def save(self, *args, **kwargs):  
            self._url_cache.clear() # Clean the local url cache dict
            return super(PageTree, self).save(*args, **kwargs)
    ---------------------------------------------------------------------------
    
    
    logging
    ~~~~~~~
    
    To enable logging, add this to your settings, e.g.:
    
        from django.utils import log
        logger = log.getLogger("django_tools.local_sync_cache")
        logger.setLevel(log.logging.DEBUG)
        logger.addHandler(log.logging.FileHandler("local_sync_cache.log"))
    
    
    :copyleft: 2011-2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys
import time
import datetime

from django.conf import settings
from django.core import cache
from django.utils import log


logger = log.getLogger("django_tools.local_sync_cache")


#if "runserver" in sys.argv or "tests" in sys.argv:
#    log.logging.basicConfig(format='%(created)f pid:%(process)d %(message)s')
#    logger.setLevel(log.logging.DEBUG)
#    logger.addHandler(log.logging.StreamHandler())


if not logger.handlers:
    # ensures we don't get any 'No handlers could be found...' messages
    logger.addHandler(log.NullHandler())


LOCAL_SYNC_CACHE_BACKEND = getattr(settings, "LOCAL_SYNC_CACHE_BACKEND", "local_sync_cache")


def _get_cache():
    """
    return django cache object.
    Try to use a own backend and fallback to 'default' if not defined in settings.CACHES
    """
    if LOCAL_SYNC_CACHE_BACKEND not in settings.CACHES:
        # TODO: Not needed in django v1.4: https://code.djangoproject.com/ticket/16410
        msg = "You should define a '%s' cache in your settings.CACHES (use default cache)" % LOCAL_SYNC_CACHE_BACKEND
        logger.critical(msg)
        cache_name = "default" # fallback to default cache entry
    else:
        cache_name = LOCAL_SYNC_CACHE_BACKEND

    backend = settings.CACHES[cache_name]["BACKEND"]
    if "dummy" in backend or "locmem" in backend:
        msg = "You should use Memcache, FileBasedCache or DatabaseCache and not: %s" % backend
        logger.critical(msg)

    django_cache = cache.get_cache(cache_name)
    logger.debug("Use django '%s' cache: %r" % (cache_name, django_cache))
    return django_cache


class LocalSyncCache(dict):
    INIT_COUNTER = {} # Counts how often __init__ used, should allways be 1!

    # Stores all existing instance, used in middleware to call check_state()
    CACHES = []

    # Store the last reset times secondary in this local thread.
    _OWN_RESET_TIMES = {}

    def __init__(self, id=None, unique_ids=True):
        if id is None:
            raise AssertionError("LocalSyncCache must take a id as argument.")

        if unique_ids:
            for existing_cache in self.CACHES:
                if id == existing_cache.id:
                    raise AssertionError(
                        "ID %r was already used! It must be unique! (Existing ids are: %s)" % (
                            id, repr([i.id for i in self.CACHES])
                        )
                    )

        self.id = id
        self.django_cache = _get_cache()
        self.last_reset = time.time() # Save last creation/reset time
        self.CACHES.append(self)

        if not self.id in self.INIT_COUNTER:
            self.INIT_COUNTER[self.id] = 1
        else:
            logger.error("Error: __init__ for %s was called to often!" % self.id)
            self.INIT_COUNTER[self.id] += 1

        self.request_counter = 0 # Counts how often check_state called (Normaly called one time per request)
        self.own_clear_counter = 0 # Counts how often clear called in this thread
        self.ext_clear_counter = 0 # Counts how often clears from external thread

        logger.debug("%r __init__" % id)

    def check_state(self):
        """
        Check if we are out-dated or not.
        Should be called at the start of a request. e.g.: by middleware
        """
        self.request_counter += 1
        global_update_time = self.django_cache.get(self.id)

        if global_update_time is None:
            if self.id in self._OWN_RESET_TIMES:
                # clear() was called in the past in this thread and it
                # is not stored in the django cache -> resave it
                logger.info("Resave %r last reset time in cache" % self.id)
                self.django_cache.set(self.id, self._OWN_RESET_TIMES[self.id])
        elif self.last_reset < global_update_time:
            # We have out-dated data -> reset dict
            self.ext_clear_counter += 1
            logger.info("%r out-dated data -> reset (global_update_time: %r - self.last_reset: %r)" % (self.id, global_update_time, self.last_reset))
            dict.clear(self)
            self.last_reset = time.time()

            if self.id in self._OWN_RESET_TIMES:
                # In this thread clear() was called in the past and now in
                # a other thread clear() was called.
                del(self._OWN_RESET_TIMES[self.id])
                logger.debug("remove %r from _OWN_RESET_TIMES" % self.id)

    def clear(self):
        """
        Must be called from the process/thread witch change the data.
            * Clear the dict
            * Save clear time in django cache and in self._OWN_RESET_TIMES
        """
        self.own_clear_counter += 1
        dict.clear(self)
        self.last_reset = time.time()
        self.django_cache.set(self.id, self.last_reset)
        logger.info("%r - dict.clear - Set global_update_time to %r" % (self.id, self.last_reset))

        # Save reset time in this thread for re-adding it to cache in check_state()
        self._OWN_RESET_TIMES[self.id] = self.last_reset

        # Check if cache worked
        cached_value = self.django_cache.get(self.id)
        if cached_value != self.last_reset:
            logger.error("Cache seems not to work: %r != %r" % (cached_value, self.last_reset))

    @staticmethod
    def get_cache_information():
        cache_information = []
        django_cache = _get_cache()
        for instance in LocalSyncCache.CACHES:
            try:
                instance_size = sys.getsizeof(instance) # New in version 2.6
            except (AttributeError, TypeError): # PyPy raised a TypeError
                instance_size = None

            id = instance.id

            cleared = id in LocalSyncCache._OWN_RESET_TIMES
            global_update_time = django_cache.get(id)

            last_reset_datetime = datetime.datetime.fromtimestamp(instance.last_reset)
            if global_update_time:
                global_update_datetime = datetime.datetime.fromtimestamp(global_update_time)
            else:
                global_update_datetime = None

            cache_information.append({
                "instance": instance,
                "length": len(instance),
                "size": instance_size,
                "cleared": cleared,
                "global_update_time": global_update_time,
                "global_update_datetime": global_update_datetime,
                "last_reset_datetime": last_reset_datetime,
                "init_counter": LocalSyncCache.INIT_COUNTER[id],
            })
        return cache_information

    @staticmethod
    def pformat_cache_information():
        output = []
        attributes = ("id", "request_counter", "own_clear_counter", "ext_clear_counter")

        cache_information = LocalSyncCache.get_cache_information()
        for item in cache_information:
            output.append(" -" * 40)

            instance = item["instance"]

            for attr in attributes:
                output.append("%22s: %s" % (attr, getattr(instance, attr)))

            for key, value in item.iteritems():
                output.append("%22s: %r" % (key, value))

        return "\n".join(output)
