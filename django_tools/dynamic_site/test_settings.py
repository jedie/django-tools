# coding: utf-8

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ":memory:"
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

MIDDLEWARE_CLASSES = (
    'dynamic_site.middleware.DynamicSiteMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',

    'dynamic_site',
    'dynamic_site.test_app',
)
SITE_ID = 1

ROOT_URLCONF = 'dynamic_site.test_app.urls'

USE_DYNAMIC_SITE_MIDDLEWARE = True
