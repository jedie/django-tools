# coding: utf-8

from __future__ import print_function

print("Use settings:", __file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = "Unittests"
ALLOWED_HOSTS = ["*"] # Allow any domain/subdomain

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
    'django_tools.dynamic_site.middleware.DynamicSiteMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',

    'django_tools',
    'django_tools.local_sync_cache',
    'django_tools.dynamic_site',
    'django_tools_test_project.django_tools_test_app',
)
SITE_ID = 1

USE_DYNAMIC_SITE_MIDDLEWARE = True

ROOT_URLCONF = 'django_tools_test_project.django_tools_test_app.urls'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(msecs)d %(module)s.%(funcName)s line %(lineno)d: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            # 'formatter': 'simple'
            'formatter': 'verbose'
        },
    },
    'loggers': {
        "django_tools": {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        "django_tools.DynamicSite": {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}