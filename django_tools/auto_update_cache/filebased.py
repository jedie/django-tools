"""
    Auto update Filebased cache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import logging
import os
import time

from django.conf import settings
from django.core.cache.backends.filebased import FileBasedCache


try:
    import pickle as pickle
except ImportError:
    import pickle


logger = logging.getLogger(__name__)


AUTOUPDATECACHE_CHANGE_TIME = getattr(settings, "AUTOUPDATECACHE_CHANGE_TIME", "AUTOUPDATECACHE_CHANGE_TIME")
AUTOUPDATECACHE_UPDATE_TIMESTAMP = getattr(settings, "AUTOUPDATECACHE_UPDATE_TIMESTAMP", 10)
AUTOUPDATECACHE_TIMES = getattr(settings, "AUTOUPDATECACHE_TIMES", (
    # load value, max age in sec.
    (0, 10),  # < 0.5     -> 10sec
    (0.5, 30),  # 0.5 - 1.0 -> 30sec
    (1.0, 60),  # 1.0 - 1.5 ->  1Min
    (1.5, 120),  # 1.5 - 2.0 ->  2Min
    (2.0, 300),  # 2.0 - 3.0 ->  5Min
    (3.0, 900),  # 3.0 - 4.0 -> 15Min
    (4.0, 3600),  # > 4.0     ->  1h
))

# Sort from biggest to lowest:
AUTOUPDATECACHE_TIMES = list(AUTOUPDATECACHE_TIMES)
AUTOUPDATECACHE_TIMES.sort(reverse=True)
AUTOUPDATECACHE_TIMES = tuple(AUTOUPDATECACHE_TIMES)


def get_max_age(load_average) -> int:
    """
    return max age for the given load average.
    >>> get_max_age(0)
    10
    >>> get_max_age(1.25)
    60
    >>> get_max_age(999)
    3600
    """
    for load, max_age in AUTOUPDATECACHE_TIMES:
        if load_average >= load:
            return max_age


class AutoUpdateFileBasedCache(FileBasedCache):
    CHANGE_TIME = None  # Timestamp of the "last update"
    NEXT_SYNC = None  # Point in the future to update the CHANGE_TIME

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import warnings
        warnings.warn(
            "django-tools AutoUpdateFileBasedCache is deprecated, use new SmoothCacheBackends!",
            category=DeprecationWarning,
            stacklevel=2,
        )

    def save_change_time(self):
        """
        save the "last change" timestamp to renew the cache entries in
        self.CHANGE_TIME and in cache.
        """
        now = time.time()
        self.CHANGE_TIME = now
        self.set(AUTOUPDATECACHE_CHANGE_TIME, now)
        logger.debug(f"Set CHANGE_TIME to {now!r}")

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

            change_time = super().get(AUTOUPDATECACHE_CHANGE_TIME)
            if change_time is None:
                logger.debug("CHANGE_TIME is None")
                self.save_change_time()  # save change time into cache
            elif change_time > self.CHANGE_TIME:
                self.CHANGE_TIME = change_time
                logger.debug(f"update change time to: {change_time!r}")
        else:
            logger.debug(f"Use old CHANGE_TIME {self.CHANGE_TIME!r}")

        return self.CHANGE_TIME

    def must_updated(self, key, create_time):
        """
        return True if given cache create time is older than the "last change"
        time, but only if the additional time from system load allows it.
        """
        last_change_time = self.get_change_time()
        if last_change_time < create_time:
            logger.debug(f"Cache item {key!r} not out-dated")
            return False

        outdate_age = last_change_time - create_time
        load_average = os.getloadavg()[0]  # load over last minute
        max_age = get_max_age(load_average)
        if outdate_age > max_age:
            logger.debug(f"Out-dated {key!r} (age: {outdate_age}, max age: {max_age}, load: {load_average})")
            return True

        logger.debug(f"Keep {key!r} by load (out-dated age: {outdate_age}, max age: {max_age}, load: {load_average})")
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
                    # ----------------------------------------------------------
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
                    # ----------------------------------------------------------
            finally:
                f.close()
        except (OSError, EOFError, pickle.PickleError):
            pass
        return default
