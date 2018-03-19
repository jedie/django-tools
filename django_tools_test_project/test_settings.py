# coding: utf-8


from __future__ import print_function

from django_tools.unittest_utils.disable_migrations import DisableMigrations


print("Use settings:", __file__)

DEBUG = True

SECRET_KEY = "Unittests"
ALLOWED_HOSTS = ["*"] # Allow any domain/subdomain

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ":memory:"
    }
}

MIGRATION_MODULES = DisableMigrations()

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_tools.dynamic_site.middleware.DynamicSiteMiddleware',
    'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware',
    'django_tools.middlewares.TracebackLogMiddleware.TracebackLogMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',

    'easy_thumbnails', 'filer', # for django_tools.unittest_utils.mockup

    'django_tools',
    'django_tools.local_sync_cache',
    'django_tools.dynamic_site',
    'django_tools_test_project.django_tools_test_app',

    'django_tools.manage_commands.django_tools_list_models',

    'django_tools.manage_commands.django_tools_nice_diffsettings',
)


from django_tools.mail.settings import *


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'loaders': [
                (
                    "django_tools.template.loader.DebugCacheLoader",
                    (
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ),
                ),
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ]
        },
    },
]

#==============================================================================

CELERY_ALWAYS_EAGER = True
BROKER_TRANSPORT = "memory"
EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'

#==============================================================================


SITE_ID = 1

USE_DYNAMIC_SITE_MIDDLEWARE = True

ROOT_URLCONF = 'django_tools_test_project.django_tools_test_app.urls'

PASSWORD_HASHERS = ( # Speedup tests
    'django.contrib.auth.hashers.MD5PasswordHasher',
)


#_____________________________________________________________________________
# cut 'pathname' in log output

import logging
try:
    old_factory = logging.getLogRecordFactory()
except AttributeError: # e.g.: Python < v3.2
    pass
else:
    def cut_path(pathname, max_length):
        if len(pathname)<=max_length:
            return pathname
        return "...%s" % pathname[-(max_length-3):]

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.pathname = cut_path(record.pathname, 30)
        return record

    logging.setLogRecordFactory(record_factory)


#-----------------------------------------------------------------------------


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)8s %(pathname)s:%(lineno)-3s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {'class': 'logging.NullHandler',},
        'console': {
            'class': 'logging.StreamHandler',
            # 'formatter': 'simple'
            'formatter': 'verbose'
        },
    },
    'loggers': {
        "django_tools": {
            'handlers': [
                'null',
                # 'console'
            ],
            'level': 'DEBUG',
        },
        "django_tools.DynamicSite": {
            'handlers': [
                'null',
                # 'console'
            ],
            'level': 'DEBUG',
        },
    },
}
