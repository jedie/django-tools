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

from django.db import models
from django.contrib.sites.models import Site
from django.utils import log
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django_tools.models import UpdateInfoBaseModel


logger = log.getLogger("django_tools.DynamicSite")
if not logger.handlers:
    # ensures we don't get any 'No handlers could be found...' messages
    logger.addHandler(log.NullHandler())


class SiteAliasManager(models.Manager):
    ALIAS_STRING_CACHE = {}
    ALIAS_REGEX_CACHE = None

    _init = False
    def get_from_host(self, current_host):
        if self.ALIAS_REGEX_CACHE is None:
            logger.debug("Fill SiteAlias cache")
            self.ALIAS_REGEX_CACHE = []
            queryset = self.all()
            for site_alias in queryset:
                if not site_alias.regex:
                    self.ALIAS_STRING_CACHE[site_alias.alias.lower()] = site_alias.site
                else: # regex:
                    regex = re.compile(site_alias.alias, re.UNICODE)
                    self.ALIAS_REGEX_CACHE.append((regex, site_alias.site))
            self.ALIAS_REGEX_CACHE = tuple(self.ALIAS_REGEX_CACHE)
            logger.debug("Alias string cache: %s" % repr(self.ALIAS_STRING_CACHE))
            logger.debug("Alias regex cache: %s" % repr(self.ALIAS_REGEX_CACHE))

        # Try first all string alias:
        try:
            return self.ALIAS_STRING_CACHE[current_host]
        except KeyError:
            logger.debug("No site found in string cache for %r" % current_host)

        # Try all regex alias:
        for regex, site in self.ALIAS_REGEX_CACHE:
            match = regex.search(current_host)
            if match is not None:
                return site

        logger.debug("No site found in regex cache for %r" % current_host)
        raise self.model.DoesNotExist("No alias found for %r" % current_host)

    def clear_cache(self):
        self.ALIAS_STRING_CACHE = {}
        self.ALIAS_REGEX_CACHE = None


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
                    re.compile(alias, re.UNICODE)
                except Exception, err:
                    message_dict["alias"] = [mark_safe(_("Regex %r is not a valid: <strong>%s</strong>") % (alias, err))]

        if message_dict:
            raise ValidationError(message_dict)

    def save(self, *args, **kwargs):
        self.clean_fields(exclude={})
        return UpdateInfoBaseModel.save(self, *args, **kwargs)
