# coding: utf-8

"""
    Auto update Filebased cache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    
    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import time
import sys
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.utils import log
from django.core.cache.backends.filebased import FileBasedCache
from django.conf import settings


AUTOUPDATECACHE_CHANGE_TIME = getattr(settings, "AUTOUPDATECACHE_CHANGE_TIME", "AUTOUPDATECACHE_CHANGE_TIME")
AUTOUPDATECACHE_UPDATE_TIMESTAMP = getattr(settings, "AUTOUPDATECACHE_UPDATE_TIMESTAMP", 10)
AUTOUPDATECACHE_TIMES = getattr(settings, "AUTOUPDATECACHE_TIMES", (
    # load value, max age in sec.
    (0, 10), #     < 0.5     -> 10sec
    (0.5, 30), #   0.5 - 1.0 -> 30sec
    (1.0, 60), #   1.0 - 1.5 ->  1Min
    (1.5, 120), #  1.5 - 2.0 ->  2Min
    (2.0, 300), #  2.0 - 3.0 ->  5Min
    (3.0, 900), #  3.0 - 4.0 -> 15Min
    (4.0, 3600), # > 4.0     ->  1h
))

# Sort from biggest to lowest:
AUTOUPDATECACHE_TIMES = list(AUTOUPDATECACHE_TIMES)
AUTOUPDATECACHE_TIMES.sort(reverse=True)
AUTOUPDATECACHE_TIMES = tuple(AUTOUPDATECACHE_TIMES)

def get_max_age(load_average):
    """ return max age for the given load average. """
    load_average += 0.1
    for load, max_age in AUTOUPDATECACHE_TIMES:
        if load_average > load:
            break
    return max_age


logger = log.getLogger("SmoothyFileBasedCache")

if "runserver" in sys.argv or "tests" in sys.argv:
    log.logging.basicConfig(format='%(created)f pid:%(process)d %(message)s')
    logger.setLevel(log.logging.DEBUG)
    logger.addHandler(log.logging.StreamHandler())

if not logger.handlers:
    # ensures we don't get any 'No handlers could be found...' messages
    logger.addHandler(log.NullHandler())


class AutoUpdateFileBasedCache(FileBasedCache):
    CHANGE_TIME = None # Timestamp of the "last update"
    NEXT_SYNC = None # Point in the future to update the CHANGE_TIME

    def save_change_time(self):
        """
        save the "last change" timestamp to renew the cache entries in
        self.CHANGE_TIME and in cache.
        """
        now = time.time()
        self.CHANGE_TIME = now
        self.set(AUTOUPDATECACHE_CHANGE_TIME, now)
        logger.debug("Set CHANGE_TIME to %r" % now)

    def get_change_time(self):
        """
        return current "last change" timestamp.
        To save cache access, update the timestamp only in  
        AUTOUPDATECACHE_UPDATE_TIMESTAMP frequency from cache.
        """
        now = time.time()
        if now > self.NEXT_SYNC or self.CHANGE_TIME is None:
            # Update timestamp we must look for a new change time from cache:
            self.NEXT_SYNC = now + AUTOUPDATECACHE_UPDATE_TIMESTAMP

            change_time = super(AutoUpdateFileBasedCache, self).get(AUTOUPDATECACHE_CHANGE_TIME)
            if change_time is None:
                logger.debug("CHANGE_TIME is None")
                self.save_change_time() # save change time into cache             
            elif change_time > self.CHANGE_TIME:
                self.CHANGE_TIME = change_time
                logger.debug("update change time to: %r" % change_time)
        else:
            logger.debug("Use old CHANGE_TIME %r" % self.CHANGE_TIME)

        return self.CHANGE_TIME

    def must_updated(self, key, create_time):
        """
        return True if given cache create time is older than the "last change"
        time, but only if the additional time from system load allows it.
        """
        last_change_time = self.get_change_time()
        if last_change_time < create_time:
            logger.debug("Cache item %r not out-dated" % key)
            return False

        outdate_age = last_change_time - create_time
        load_average = os.getloadavg()[0] # load over last minute
        max_age = get_max_age(load_average)
        if outdate_age > max_age:
            logger.debug("Out-dated %r (age: %s, max age: %s, load: %s)" % (
                key, outdate_age, max_age, load_average
            ))
            return True

        logger.debug("Keep %r by load (out-dated age: %s, max age: %s, load: %s)" % (
            key, outdate_age, max_age, load_average
        ))
        return False

    def get(self, key, default=None, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)

        fname = self._key_to_file(key)
        try:
            f = open(fname, 'rb')
            try:
                exp = pickle.load(f)
                now = time.time()
                if exp < now:
                    self._delete(fname)
                else:
                    #----------------------------------------------------------
                    # START area of changes to the original get() method.
                    #
                    # Use the modify time of the cache file and
                    # compare it with the "last change" time. 
                    mtime = os.fstat(f.fileno()).st_mtime
                    if self.must_updated(key, mtime):
                        self._delete(fname)
                    else:
                        return pickle.load(f)

                    # END area of changes to the original function.
                    #----------------------------------------------------------
            finally:
                f.close()
        except (IOError, OSError, EOFError, pickle.PickleError):
            pass
        return default

