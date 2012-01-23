# coding:utf-8

"""
    Dynamic SITE ID
    ~~~~~~~~~~~~~~~
    
    Set the SITE_ID dynamic by the current Domain Name.
    
    +++ experimental, yet! +++
    
    Sourcecode parts are borrowed from:
    
    * http://bitbucket.org/uysrc/django-dynamicsites/
    * Patches in http://code.djangoproject.com/ticket/4438
    * http://djangosnippets.org/snippets/1099/
    
    See also:
    
    * http://groups.google.com/group/django-developers/browse_thread/thread/4125cb192c72ed59/
    * http://groups.google.com/group/django-developers/browse_thread/thread/d9f1088de7944de3/

    usage
    ~~~~~
    
    Add DynamicSiteMiddleware as the first middleware to settings, e.g:
    ---------------------------------------------------------------------------
        MIDDLEWARE_CLASSES = (
            'django_tools.middlewares.DynamicSite.DynamicSiteMiddleware',
            ...
        )
        
    # activate django-tools DynamicSiteMiddleware:
    USE_DYNAMIC_SITE_MIDDLEWARE = True
    ---------------------------------------------------------------------------
    
    
    Note: Dynamic SITE ID is problematic in unittests. To avoid this, add theses
    lines in you test runner file:
    ---------------------------------------------------------------------------
    from django.conf import settings
    
    # Disable dynamic site, if used:
    if getattr(settings, "USE_DYNAMIC_SITE_MIDDLEWARE", False):
        settings.USE_DYNAMIC_SITE_MIDDLEWARE = False
        settings.SITE_ID = 1 
    ---------------------------------------------------------------------------    


    :copyleft: 2011-2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import sys
import warnings

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from django.conf import settings
from django.contrib.sites import models as sites_models
from django.core.exceptions import MiddlewareNotUsed
from django.utils import log

from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache


logger = log.getLogger("django_tools.DynamicSite")

#if "runserver" in sys.argv or "tests" in sys.argv:
#    log.logging.basicConfig(format='%(created)f pid:%(process)d %(message)s')
#    logger.setLevel(log.logging.DEBUG)
#    logger.addHandler(log.logging.StreamHandler())

if not logger.handlers:
    # ensures we don't get any 'No handlers could be found...' messages
    logger.addHandler(log.NullHandler())


Site = sites_models.Site # Shortcut

# Use the same SITE_CACHE for getting site object by host [1] and get current site by SITE_ID [2]
# [1] here in DynamicSiteMiddleware._get_site_id_from_host()
# [2] in django.contrib.sites.models.SiteManager.get_current()
SITE_CACHE = LocalSyncCache(id="DynamicSite cache")
sites_models.SITE_CACHE = SITE_CACHE

SITE_THREAD_LOCAL = local()

# Use Fallback ID if host not exist in Site table. We use int() here, because
# os environment variables are always strings.
FALLBACK_SITE_ID = int(getattr(os.environ, "SITE_ID", settings.SITE_ID))
logger.debug("Fallback SITE_ID: %r" % FALLBACK_SITE_ID)

# Use Fallback ID at startup before process_request(), e.g. in unittests
SITE_THREAD_LOCAL.SITE_ID = FALLBACK_SITE_ID


class DynamicSiteId(object):
    def __getattribute__(self, name):
#        print "DynamicSiteId __getattribute__", name
        return getattr(SITE_THREAD_LOCAL.SITE_ID, name)
    def __int__(self):
#        print "DynamicSiteId __int__"
        return SITE_THREAD_LOCAL.SITE_ID
    def __hash__(self):
#        print "DynamicSiteId __hash__"
        return hash(SITE_THREAD_LOCAL.SITE_ID)
    def __repr__(self):
#        print "DynamicSiteId __repr__"
        return repr(SITE_THREAD_LOCAL.SITE_ID)
    def __str__(self):
#        print "DynamicSiteId __str__"
        return str(SITE_THREAD_LOCAL.SITE_ID)
    def __unicode__(self):
#        print "DynamicSiteId __unicode__"
        return unicode(SITE_THREAD_LOCAL.SITE_ID)


settings.SITE_ID = DynamicSiteId()

# Use the same cache for Site.objects.get_current():
sites_models.SITE_CACHE = SITE_CACHE


def _clear_cache(self):
    logger.debug("Clear SITE_CACHE (The django-tools LocalSyncCache() dict)")
    SITE_CACHE.clear()

# monkey patch for django.contrib.sites.models.SiteManager.clear_cache
sites_models.SiteManager.clear_cache = _clear_cache


class DynamicSiteMiddleware(object):
    """ Set settings.SITE_ID based on request's domain. """

    def __init__(self):
        # User must add "USE_DYNAMIC_SITE_MIDDLEWARE = True" in his local_settings.py
        # to activate this middleware
        if not getattr(settings, "USE_DYNAMIC_SITE_MIDDLEWARE", False) == True:
            logger.info("DynamicSiteMiddleware is deactivated.")
            raise MiddlewareNotUsed()
        else:
            logger.info("DynamicSiteMiddleware is active.")

    def process_request(self, request):
        # Get django.contrib.sites.models.Site instance by the current domain name:
        site = self._get_site_id_from_host(request)

        # Save the current site
        SITE_THREAD_LOCAL.SITE_ID = site.pk

        # Put site in cache for django.contrib.sites.models.SiteManager.get_current():
        SITE_CACHE[SITE_THREAD_LOCAL.SITE_ID] = site

#        def test():
#            from django.contrib.sites.models import Site, SITE_CACHE
#            from django.conf import settings
#            print id(SITE_CACHE), SITE_CACHE
#            print "-"*79
#            for k, v in SITE_CACHE.items():
#                print k, type(k), id(k), hash(k), v
#            print "-"*79
#            print id(settings.SITE_ID), settings.SITE_ID
#            print "TEST:", Site.objects.get_current()
#        test()

    def _get_site_id_from_host(self, request):
        host = request.get_host().lower()
        try:
            return SITE_CACHE[host]
        except KeyError:
            try:
                site = Site.objects.get(domain__iexact=host)
            except Site.DoesNotExist:
                # FIXME: How can we give better feedback?
                all_sites = Site.objects.all()
                msg = "Error: There exist no SITE entry for domain %r! (Existing domains: %s)" % (
                    host, repr(all_sites.values_list("domain", flat=True))
                )
                logger.critical(msg)
#                if settings.DEBUG:
#                    raise RuntimeError(msg)
#                else:
                warnings.warn(msg)

                # Fallback:
                site = Site.objects.get(id=FALLBACK_SITE_ID)
            else:
                logger.debug("Set site to %r for %r" % (site, host))
                SITE_CACHE[host] = site

            return site



