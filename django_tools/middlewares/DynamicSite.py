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
    ---------------------------------------------------------------------------

    :copyleft: 2011-2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import warnings

from django.conf import settings
from django.contrib.sites import models as sites_models
Site = sites_models.Site

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache

# Fallback SITE_ID:
FALLBACK_SITE_ID = getattr(os.environ, "SITE_ID", settings.SITE_ID)


SITE_CACHE = LocalSyncCache(id="DynamicSite cache")

# Use the same SITE_CACHE for getting site object by host [1] and get current site by SITE_ID [2]
# [1] here in DynamicSiteMiddleware._get_site_id_from_host()
# [2] in django.contrib.sites.models.SiteManager.get_current()
sites_models.SITE_CACHE = SITE_CACHE

SITE_THREAD_LOCAL = local()

# Use Fallback ID if Request not started e.g. in unittests
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
    """ Clear django-tools LocalSyncCache() dict """
    print "Use own clear!"
    SITE_CACHE.clear()

# monkey patch for django.contrib.sites.models.SiteManager.clear_cache
sites_models.SiteManager.clear_cache = _clear_cache


class DynamicSiteMiddleware(object):
    """ Set settings.SITE_ID based on request's domain. """

    def process_request(self, request):
        site = self._get_site_id_from_host(request)
        SITE_THREAD_LOCAL.SITE_ID = site.pk
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
#                if settings.DEBUG:
#                    raise RuntimeError(msg)
#                else:
                warnings.warn(msg)

                # Fallback:
                site = Site.objects.get(id=FALLBACK_SITE_ID)
            else:
                print "Set site to %r for %r" % (site, host)
                SITE_CACHE[host] = site

            return site



