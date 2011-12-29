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

    :copyleft: 2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import logging
from django.contrib.sites.models import RequestSite, Site, SITE_CACHE, SiteManager
from django.contrib.sites import models as sites_models
from django.contrib import messages
import warnings

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache

from django.conf import settings


SITE_CACHE = LocalSyncCache(id="DynamicSite cache")
SITE_THREAD_LOCAL = local()
SITE_THREAD_LOCAL.SITE_ID = 1 # Fallback, ID should be exist.


class DynamicSiteId(object):
    def __getattribute__(self, name):
        return getattr(SITE_THREAD_LOCAL.SITE_ID, name)
#    def __int__(self):
#        return SITE_THREAD_LOCAL.SITE_ID
#    def __value__(self):
#        return SITE_THREAD_LOCAL.SITE_ID
#    def __hash__(self):
#        return hash(SITE_THREAD_LOCAL.SITE_ID)
#    def __id__(self):
#        return id(SITE_THREAD_LOCAL.SITE_ID)
#    def __repr__(self):
#        return str(SITE_THREAD_LOCAL.SITE_ID)
#    def __str__(self):
#        return str(SITE_THREAD_LOCAL.SITE_ID)
#    def __unicode__(self):
#        return unicode(SITE_THREAD_LOCAL.SITE_ID)


settings.SITE_ID = DynamicSiteId()

# Use the same cache for Site.objects.get_current():
sites_models.SITE_CACHE = SITE_CACHE


def _clear_cache(self):
    print "Use own clear!"
    SITE_CACHE.clear()

SiteManager.clear_cache = _clear_cache


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
            matches = Site.objects.filter(domain__iexact=host)
            # We use len rather than count to save a second query if there was only one matching Site
            count = len(matches)
            if count == 1:
                # Return the single matching Site
                site = matches[0]
                print "Set site to %r for %r" % (site, host)
                SITE_CACHE[host] = site
            else:
                # FIXME: How can we give better feedback?
                msg = "Error: There exist not SITE entry for domain %r! (Existing domains: %s)" % (
                    host, repr(Site.objects.all().values_list("domain", flat=True))
                )
                if settings.DEBUG:
                    raise RuntimeError(msg)
                else:
                    warnings.warn(msg)
                # Fallback
                site = Site.objects.all()[1]

            return site


