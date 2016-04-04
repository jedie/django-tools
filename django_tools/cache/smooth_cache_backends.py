# coding: utf-8

"""
    smooth cache backends
    ~~~~~~~~~~~~~~~~~~~~~

    more information in the README.

    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import logging
import os
import time

if __name__ == "__main__":
    # For doctest only
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

from django.conf import settings
from django.core.cache.backends.db import DatabaseCache
from django.core.cache.backends.filebased import FileBasedCache
from django.core.cache.backends.locmem import LocMemCache
from django.core.cache.backends.memcached import MemcachedCache, PyLibMCCache



logger = logging.getLogger("django-tools.SmoothCache")
if not logger.handlers:
    # ensures we don't get any 'No handlers could be found...' messages
    logger.addHandler(logging.NullHandler())

#if "runserver" in sys.argv or "tests" in sys.argv:
#    log.logging.basicConfig(format='%(created)f pid:%(process)d %(message)s')
#    logger.setLevel(log.logging.DEBUG)
#    logger.addHandler(log.logging.StreamHandler())


SMOOTH_CACHE_CHANGE_TIME = getattr(settings, "SMOOTH_CACHE_CHANGE_TIME", "DJANGO_TOOLS_SMOOTH_CACHE_CHANGE_TIME")
SMOOTH_CACHE_UPDATE_TIMESTAMP = getattr(settings, "SMOOTH_CACHE_UPDATE_TIMESTAMP", 10)
SMOOTH_CACHE_TIMES = getattr(settings, "SMOOTH_CACHE_TIMES", (
    # load value, max age in sec.
    (0, 5), #          < 0.1 ->  5sec
    (0.1, 10), #   0.1 - 0.5 -> 10sec
    (0.5, 30), #   0.5 - 1.0 -> 30sec
    (1.0, 60), #   1.0 - 1.5 ->  1Min
    (1.5, 120), #  1.5 - 2.0 ->  2Min
    (2.0, 300), #  2.0 - 3.0 ->  5Min
    (3.0, 900), #  3.0 - 4.0 -> 15Min
    (4.0, 3600), #     > 4.0 ->  1h
))

# Sort from biggest to lowest:
SMOOTH_CACHE_TIMES = list(SMOOTH_CACHE_TIMES)
SMOOTH_CACHE_TIMES.sort(reverse=True)
SMOOTH_CACHE_TIMES = tuple(SMOOTH_CACHE_TIMES)


def get_max_age(load_average):
    """
    return max age for the given load average.

    >>> get_max_age(0)
    5
    >>> get_max_age(0.09)
    5
    >>> get_max_age(0.1)
    5
    >>> get_max_age(0.11)
    10
    """
    for load, max_age in SMOOTH_CACHE_TIMES:
        if load_average > load:
            break
    return max_age


class SmoothCacheTime(int):
    def __new__(cls, value=None):
        if value is None:
            value = time.time()
        i = int.__new__(cls, value)
        return i


class _SmoothCache(object):
    __CHANGE_TIME = None # Timestamp of the "last update"
    __NEXT_SYNC = None # Point in the future to update the __CHANGE_TIME

    def __init__(self, *args, **kwargs):
        super(_SmoothCache, self).__init__(*args, **kwargs)
        self._smooth_clear = None

    def __get_change_time(self):
        """
        return current "last change" timestamp.
        To save cache access, update the timestamp only in
        SMOOTH_CACHE_UPDATE_TIMESTAMP frequency from cache.
        """
        now = time.time()
        if now > self.__NEXT_SYNC or self.__CHANGE_TIME is None:
            # Update timestamp we must look for a new change time from cache:
            self.__NEXT_SYNC = now + SMOOTH_CACHE_UPDATE_TIMESTAMP

            # use raw method, otherwise: end in a endless-loop ;)
            change_time = self.get(SMOOTH_CACHE_CHANGE_TIME, raw=True)
            if change_time is None:
                logger.debug("CHANGE_TIME is None")
                self.smooth_update() # save change time into cache
            elif change_time > self.__CHANGE_TIME:
                self.__CHANGE_TIME = change_time
                logger.debug("update change time to: %r" % change_time)
#        else:
#            logger.debug("Use old CHANGE_TIME %r" % self.__CHANGE_TIME)

        return self.__CHANGE_TIME

    def __must_updated(self, key, create_time):
        """
        return True if given cache create time is older than the "last change"
        time, but only if the additional time from system load allows it.
        """
        last_change_time = self.__get_change_time()
        if last_change_time < create_time:
            # Item was added to the cache after the last clear() time.
            logger.debug(
                "%r not out-dated: added %ssec before clear()" % (
                    key, (create_time - last_change_time)
            ))
            return False

        outdate_age = time.time() - last_change_time
        load_average = os.getloadavg()[0] # load over last minute
        max_age = get_max_age(load_average)
        if outdate_age > max_age:
            logger.debug("Out-dated %r (added %ssec after clear() - age: %s, max age: %s, load: %s)" % (
                key, (last_change_time - create_time), outdate_age, max_age, load_average
            ))
            return True
        else:
            logger.debug("Keep %r by load (out-dated age: %.1fsec, max age: %s, load: %s)" % (
                key, outdate_age, max_age, load_average
            ))
            return False

    def smooth_update(self):
        """
        save the "last change" timestamp to renew the cache entries in
        self.__CHANGE_TIME and in cache.
        """
        now = int(time.time())
        self.__CHANGE_TIME = now
        self.set(SMOOTH_CACHE_CHANGE_TIME, now, raw=True) # will be get via __origin_get()
        logger.debug("Set CHANGE_TIME to %r" % now)

    #--------------------------------------------------------------------------

    def get(self, key, default=None, version=None, raw=False):
        value = super(_SmoothCache, self).get(key, default, version)
        if raw:
            return value
        if value is None or value is default:
            # Item not in cache
            return value

        try:
            create_time, value = value
            assert isinstance(create_time, SmoothCacheTime), (
                "create_time is not SmoothCacheTime instance, it's: %s" % type(create_time)
            )
        except Exception as err:
            # e.g: entry is saved before smooth cache used.
            logger.error("Can't get 'create_time' from: %s (Maybe %r is a old cache entry?)" % (err, key))
            self.delete(key, version)
            return default

        if self.__must_updated(key, create_time):
            # is too old -> delete the item
            self.delete(key, version)
            return default

        return value

    def set(self, key, value, timeout=None, version=None, raw=False):
        if not raw:
            value = (SmoothCacheTime(), value)
        super(_SmoothCache, self).set(key, value, timeout, version)

    def clear(self):
        logger.debug("SmoothCache clear called!")
        super(_SmoothCache, self).clear()
        self.smooth_update()


class SmoothFileBasedCache(_SmoothCache, FileBasedCache):
    pass

class SmoothDatabaseCache(_SmoothCache, DatabaseCache):
    pass

class SmoothLocMemCache(_SmoothCache, LocMemCache):
    pass

class SmoothMemcachedCache(_SmoothCache, MemcachedCache):
    pass

class SmoothPyLibMCCache(_SmoothCache, PyLibMCCache):
    pass


if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
