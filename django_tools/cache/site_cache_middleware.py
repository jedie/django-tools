# coding: utf-8

"""
    per-site cache middleware
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    more information in the README.

    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import logging
import sys

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.cache import get_max_age, patch_response_headers

from django_tools.utils.importlib import get_attr_from_settings


logger = logging.getLogger("django-tools.CacheMiddleware")

CACHE_MIDDLEWARE_ANONYMOUS_ONLY = getattr(settings, 'CACHE_MIDDLEWARE_ANONYMOUS_ONLY', False)
RUN_WITH_DEV_SERVER = getattr(settings, "RUN_WITH_DEV_SERVER", "runserver" in sys.argv)
EXTRA_DEBUG = getattr(settings, "CACHE_EXTRA_DEBUG", False)

COUNT_FETCH_FROM_CACHE = getattr(settings, "COUNT_FETCH_FROM_CACHE", False)
COUNT_UPDATE_CACHE = getattr(settings, "COUNT_UPDATE_CACHE", False)
COUNT_IN_CACHE = getattr(settings, "COUNT_IN_CACHE", False)

cache_callback = get_attr_from_settings("CACHE_CALLBACK", "DjangoTools cache callback")
logger.debug("Use cache callback: %s" % repr(cache_callback))


CACHE_REQUESTS = "DJANGOTOOLS_CACHE_REQUESTS_COUNT"
CACHE_REQUEST_HITS = "DJANGOTOOLS_CACHE_REQUEST_HITS_COUNT"
CACHE_RESPONSES = "DJANGOTOOLS_CACHE_RESPONSES_COUNT"
CACHE_RESPONSE_HITS = "DJANGOTOOLS_CACHE_RESPONSE_HITS_COUNT"

_CACHE_KEYS = (CACHE_REQUESTS, CACHE_REQUEST_HITS, CACHE_RESPONSES, CACHE_RESPONSE_HITS)


# Some information from the cache usage.
# Note: These values are only for current process/thread valid and they not thread safe!
# Set settings.COUNT_IN_CACHE=True for process/thread safe counting.
LOCAL_CACHE_INFO = {
    # from FetchFromCacheMiddleware:
    "requests": None, # total numbers of requests
    "request hits": None, # number of cache hits

    # from UpdateCacheMiddleware:
    "responses": None, # total numbers of responses
    "response hits": None, # number of responses from cache
}


def init_cache_counting():
    """
    prepare LOCAL_CACHE_INFO and the counter in cache:
    All initial count value should be None, if count is disabled
    and should be 0, if enabled.
    """
    for key in _CACHE_KEYS:
        cache.delete(key) # delete old entrie, if exist

    if COUNT_FETCH_FROM_CACHE:
        # Count in FetchFromCacheMiddleware is enabled
        LOCAL_CACHE_INFO["requests"] = 0
        LOCAL_CACHE_INFO["request hits"] = 0
        if COUNT_IN_CACHE:
            # Count in cache is enabled
            cache.set(CACHE_REQUESTS, 0)
            cache.set(CACHE_REQUEST_HITS, 0)

    if COUNT_UPDATE_CACHE:
        # Count in UpdateCacheMiddleware is enabled
        LOCAL_CACHE_INFO["responses"] = 0
        LOCAL_CACHE_INFO["response hits"] = 0
        if COUNT_IN_CACHE:
            # Count in cache is enabled
            cache.set(CACHE_RESPONSES, 0)
            cache.set(CACHE_RESPONSE_HITS, 0)

init_cache_counting()


def build_cache_key(url, language_code, site_id):
    cache_key = "%s:%s:%s" % (url, language_code, site_id)
    if EXTRA_DEBUG:
        logger.debug("Cache key: %r" % cache_key)
    return cache_key


def get_cache_key(request):
    """
    Build the cache key based on the url and:

    * LANGUAGE_CODE: The language code in the url can be different than the
        used language for gettext translation.
    * SITE_ID: request.path is the url without the domain name. So the same
        url in site A and B would result in a collision.
    """
    url = request.get_full_path()

    try:
        language_code = request.LANGUAGE_CODE # set in django.middleware.locale.LocaleMiddleware
    except AttributeError:
        etype, evalue, etb = sys.exc_info()
        evalue = etype("%s (django.middleware.locale.LocaleMiddleware must be insert before cache middleware!)" % evalue)
        raise etype(evalue).with_traceback(etb)

    site_id = settings.SITE_ID
    cache_key = build_cache_key(url, language_code, site_id)
    return cache_key


def delete_cache_item(url, language_code, site_id=None):
    if site_id is None:
        site_id = settings.SITE_ID

    cache_key = build_cache_key(url, language_code, site_id)
    logger.debug("delete from cache: %r" % cache_key)
    cache.delete(cache_key)


class CacheMiddlewareBase(object):
    def use_cache(self, request, response=None):
        if not request.method in ('GET', 'HEAD'):
            logger.debug("Don't cache %r (%s)" % (request.method, request.get_full_path()))
            return False

        if RUN_WITH_DEV_SERVER and request.path.startswith(settings.STATIC_URL):
            if EXTRA_DEBUG:
                logger.debug("Don't cache static files in dev server")
            return False

        if response and response.status_code != 200:
            logger.debug("Don't cache response with status code: %s (%s)" % (response.status_code, request.get_full_path()))
            return False

        if CACHE_MIDDLEWARE_ANONYMOUS_ONLY and request.user.is_authenticated():
            logger.debug("Don't cache requests from authenticated users.")
            return False

        if hasattr(request, '_messages') and len(request._messages) != 0:
            msg = "Don't cache: page for anonymous users has messages."
            if settings.DEBUG:
                storage = messages.get_messages(request)
                raw_messages = ", ".join([message.message for message in storage])
                storage.used = False
                msg += " (messages: %s)" % raw_messages
            logger.debug(msg)
            return False

        if response and getattr(response, 'csrf_processing_done', False):
            logger.debug("Don't cache because response.csrf_processing_done==True (e.g.: view use @csrf_protect decorator)")
            return False

        if cache_callback:
            return cache_callback(request, response)

        return True


def save_incr(key, default=1):
    try:
        cache.incr(key)
    except ValueError: # Doesn't exist, yet.
        cache.set(key, default)


class FetchFromCacheMiddleware(CacheMiddlewareBase):
    def _count_requests(self, request):
        if RUN_WITH_DEV_SERVER and request.path.startswith(settings.STATIC_URL):
            return

        LOCAL_CACHE_INFO["requests"] += 1
        if COUNT_IN_CACHE:
            save_incr(CACHE_REQUESTS)

    def _count_hit(self):
        LOCAL_CACHE_INFO["request hits"] += 1
        if COUNT_IN_CACHE:
            save_incr(CACHE_REQUEST_HITS)

    def process_request(self, request):
        """
        Try to fetch response from cache, if exists.
        """
        if COUNT_FETCH_FROM_CACHE:
            self._count_requests(request)

        if not self.use_cache(request):
            if EXTRA_DEBUG:
                logger.debug("Don't fetch from cache: %s" % request.get_full_path())
            return

        cache_key = get_cache_key(request)
        response = cache.get(cache_key)
        if response is None:
            logger.debug("Not found in cache: %r" % cache_key)
        else:
            logger.debug("Use %r from cache!" % cache_key)
            if COUNT_FETCH_FROM_CACHE:
                self._count_hit()
            response._from_cache = True
            return response


class UpdateCacheMiddleware(CacheMiddlewareBase):
    def _count_response(self, request):
        if RUN_WITH_DEV_SERVER and request.path.startswith(settings.STATIC_URL):
            return

        LOCAL_CACHE_INFO["responses"] += 1
        if COUNT_IN_CACHE:
            save_incr(CACHE_RESPONSES)

    def _count_hit(self):
        LOCAL_CACHE_INFO["response hits"] += 1
        save_incr(CACHE_RESPONSE_HITS)

    def process_response(self, request, response):
        if COUNT_UPDATE_CACHE:
            self._count_response(request)

        if getattr(response, "_from_cache", False) == True:
            if COUNT_UPDATE_CACHE:
                self._count_hit()
            logger.debug("response comes from the cache, no need to update the cache")
            return response
        else:
            # used e.g. in unittests
            response._from_cache = False

        if not self.use_cache(request, response):
            if EXTRA_DEBUG:
                logger.debug("Don't put to cache: %s" % request.get_full_path())
            return response

        # get the timeout from the "max-age" section of the "Cache-Control" header
        timeout = get_max_age(response)
        if timeout == None:
            # use default cache_timeout
            timeout = settings.CACHE_MIDDLEWARE_SECONDS
        elif timeout == 0:
            logger.debug("Don't cache this page (timeout == 0)")
            return response

        # Create a new HttpResponse for the cache, so we can skip existing
        # cookies and attributes like response.csrf_processing_done
        response2 = HttpResponse(
            content=response._container,
            status=200,
            content_type=response['Content-Type'],
        )
        if response.has_header("Content-Language"):
            response2['Content-Language'] = response['Content-Language']

        if settings.DEBUG or RUN_WITH_DEV_SERVER or request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            # Check if we store a {% csrf_token %} into the cache, this should never happen!
            for content in response._container:
                if "csrfmiddlewaretoken" in content:
                    raise AssertionError("csrf_token would be put into the cache! content: %r" % content)

        # Adds ETag, Last-Modified, Expires and Cache-Control headers
        patch_response_headers(response2, timeout)

        cache_key = get_cache_key(request)
        cache.set(cache_key, response2, timeout)

        logger.debug("Put to cache: %r" % cache_key)
        return response
