# coding: utf-8

"""
    django-tools import helper
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    additional helper to the existing django.utils.importlib

    :copyleft: 2012-2016 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import logging
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


logger = logging.getLogger("DjangoToolsImportLib")


def get_attr_from_string(path, obj_name=""):
    """
    Return a attribute from a module by the given path string.

    >>> get_attr_from_string("django_tools.cache.site_cache_middleware.UpdateCacheMiddleware")
    <class 'django_tools.cache.site_cache_middleware.UpdateCacheMiddleware'>
    """
    try:
        module_name, class_name = path.rsplit('.', 1)
    except ValueError:
        raise ImproperlyConfigured("%s isn't a %s module" % (path, obj_name))

    try:
        mod = import_module(module_name)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing %s module %s: "%s"' % (obj_name, module_name, e))

    try:
        attr = getattr(mod, class_name)
    except AttributeError:
        raise ImproperlyConfigured('%s module "%s" does not define a "%s" class' % (obj_name, module_name, class_name))

    return attr


def get_class_instance(path, obj_name=""):
    """
    Returns a class instance from a module by the given path string.

    >>> get_class_instance("django_tools.cache.site_cache_middleware.UpdateCacheMiddleware") # doctest: +ELLIPSIS
    <django_tools.cache.site_cache_middleware.UpdateCacheMiddleware object at ...>
    """
    class_obj = get_attr_from_string(path, obj_name)
    class_instance = class_obj()
    return class_instance


def get_setting(setting_name):
    """
    return the settings value, create debug log if not set/empty.

    >>> get_setting("EMAIL_BACKEND")
    'django.core.mail.backends.locmem.EmailBackend'
    """
    path = getattr(settings, setting_name, None)
    if path:
        return path
    else:
        if not hasattr(settings, setting_name):
            logger.debug("%r not in settings defined" % setting_name)
        else:
            logger.debug("settings.%s is None or empty" % setting_name)


def get_attr_from_settings(setting_name, obj_name=""):
    """
    returns a attribute from the given settings path string.

    >>> get_attr_from_settings("EMAIL_BACKEND", "email backend")
    <class 'django.core.mail.backends.locmem.EmailBackend'>
    """
    path = get_setting(setting_name)
    if path:
        return get_attr_from_string(path, obj_name)


def get_class_instance_from_settings(setting_name, obj_name=""):
    """
    returns a class instance from the given settings path string.

    >>> get_class_instance_from_settings("EMAIL_BACKEND", "email backend") # doctest: +ELLIPSIS
    <django.core.mail.backends.locmem.EmailBackend object at ...>
    """
    path = get_setting(setting_name)
    if path:
        return get_class_instance(path, obj_name)



