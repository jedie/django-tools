"""
    :created: 21.08.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import time

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache

log = logging.getLogger(__name__)


class DelayBase:
    """
    Delay something via time.sleep() and used delay value from GET parameters.

    This is only the base class, use:
        - SessionDelay()
    or
        - CacheDelay()
    """
    backend_name = None

    def __init__(self, key, only_debug=True):
        """
        :param key: session/cache key for store the delay value into backend
        :param only_debug: If True: delay only if settings.DEBUG == True
        """
        self.key = key
        self.only_debug = only_debug

    def _delete(self):
        raise NotImplementedError

    def _set(self, sec):
        raise NotImplementedError

    def _get(self):
        raise NotImplementedError

    def load(self, request, query_string, default=5):
        """
        :param query_string: the request.GET key that activate/set delay value
        :param default: fallback if no value in GET
        """
        if query_string not in request.GET:
            if self._get():
                log.debug("Delete %r delay from %s", self.key, self.backend_name)
            self._delete()
            return

        if self.only_debug and not settings.DEBUG:
            log.debug("Ignore ?%s, because DEBUG is not ON!", query_string)
            self._delete()
            return

        log.info("Add '%s' value to %s", query_string, self.backend_name)
        sec = request.GET[query_string]
        if not sec:
            sec = default
        else:
            try:
                sec = int(sec)
            except ValueError:
                sec = float(sec)
        log.warning("Save %s sec. from %r for %r into %s", sec, query_string, self.key, self.backend_name)

        if request.user.is_authenticated:
            messages.warning(request, "Use %s sec. %r" % (sec, query_string))

        self._set(sec)

    def sleep(self):
        sec = self._get()

        if sec is None:
            log.debug("No delay for %r from %s", self.key, self.backend_name)
            return

        log.warning("Delay %s sec. for %r", sec, self.key)
        time.sleep(sec)


class SessionDelay(DelayBase):
    """
    Delay via time.sleep() something, use the sleep seconds from GET parameter.
    Store the sleep seconds into request.session
    """
    backend_name = "session"

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def _delete(self):
        try:
            del self.request.session[self.key]
        except KeyError:
            pass

    def _set(self, sec):
        self.request.session[self.key] = sec

    def _get(self):
        return self.request.session.get(self.key)


class CacheDelay(DelayBase):
    """
    Delay via time.sleep() something, use the sleep seconds from GET parameter.
    Store the sleep seconds into django cache backend
    """
    backend_name = "cache"

    def __init__(self, *args, cache_timeout=30 * 60, **kwargs):
        """
        :param cache_timeout: timeout, in seconds, to use for the cache.

        You can set TIMEOUT to None so that, by default, cache keys never expire.
        see also:
            https://docs.djangoproject.com/en/1.11/topics/cache/#cache-arguments
        """
        super().__init__(*args, **kwargs)
        self.cache_timeout = cache_timeout

    def _delete(self):
        cache.delete(self.key)

    def _set(self, sec):
        cache.set(self.key, sec, self.cache_timeout)

    def _get(self):
        return cache.get(self.key)
