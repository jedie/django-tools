# coding:utf-8

"""
    Dynamic SITE ID
    ~~~~~~~~~~~~~~~
    
    Set the SITE_ID dynamic by the current Domain Name.
    
    More info: read .../django_tools/dynamic_site/README.creole
    
    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import re

from django.contrib.sites import models as sites_models
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils import log
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache
from django_tools.models import UpdateInfoBaseModel


logger = log.getLogger("django_tools.DynamicSite")
if not logger.handlers:
    # ensures we don't get any 'No handlers could be found...' messages
    logger.addHandler(log.NullHandler())


def compile_alias(alias):
    regex = re.compile(alias, re.UNICODE)
    return regex


class SiteAliasManager(models.Manager):
    ALIAS_CACHE = None

    def get_from_host(self, current_host):
        if self.ALIAS_CACHE is None:
            # first request after startup / model.save() -> fill the cache
            logger.debug("init LocalSyncCache for SiteAlias cache")
            self.ALIAS_CACHE = LocalSyncCache(id="SiteAliasCache")

        if "string" not in self.ALIAS_CACHE:
            logger.debug("Fill SiteAlias cache")
            self.ALIAS_CACHE["string"] = {}
            self.ALIAS_CACHE["regex"] = []
            queryset = self.all()
            for site_alias in queryset:
                site = site_alias.site
                alias = site_alias.alias

                if site_alias.regex:
                    regex = compile_alias(alias)
                    self.ALIAS_CACHE["regex"].append((regex, site))
                else:
                    self.ALIAS_CACHE["string"][alias.lower()] = site

            self.ALIAS_CACHE["regex"] = tuple(self.ALIAS_CACHE["regex"])
            logger.debug("Alias string cache: %s" % repr(self.ALIAS_CACHE["string"]))
            logger.debug("Alias regex cache: %s" % repr(self.ALIAS_CACHE["regex"]))

        # Try first all string alias:
        try:
            return self.ALIAS_CACHE["string"][current_host]
        except KeyError:
            logger.debug("No site found in string cache for %r" % current_host)

        # Try all regex alias:
        for regex, site in self.ALIAS_CACHE["regex"]:
            match = regex.search(current_host)
            if match is not None:
                return site

        logger.debug("No site found in regex cache for %r" % current_host)
        raise self.model.DoesNotExist("No alias found for %r" % current_host)

    def clear_cache(self):
        if self.ALIAS_CACHE is not None:
            logger.debug("Clear SiteAlias cache")
            self.ALIAS_CACHE.clear()
            logger.debug("Clear DynamicSiteMiddlewareCache cache")
            sites_models.SITE_CACHE.clear()


class SiteAlias(UpdateInfoBaseModel):
    site = models.ForeignKey(Site)
    alias = models.CharField(max_length=256,
        help_text=_("A domain name alias for the site.")
    )
    regex = models.BooleanField(default=False,
        help_text=_("Is the given domain name alias a python regular expression?")
    )
    objects = SiteAliasManager()

    def clean_fields(self, exclude):
        message_dict = {}

        if "alias" not in exclude and "regex" not in exclude:
            if self.regex:
                alias = self.alias
                try:
                    compile_alias(alias)
                except Exception, err:
                    message_dict["alias"] = [mark_safe(_("Regex %r is not a valid: <strong>%s</strong>") % (alias, err))]

        if message_dict:
            raise ValidationError(message_dict)

    def save(self, *args, **kwargs):
        self.clean_fields(exclude={})
        UpdateInfoBaseModel.save(self, *args, **kwargs)
        SiteAlias.objects.clear_cache()

    class Meta:
        verbose_name = "site alias"
        verbose_name_plural = "site aliases"


