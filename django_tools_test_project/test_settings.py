# coding: utf-8
import os

print("Use settings:", __file__)

import logging
import warnings

from django.utils.translation import ugettext_lazy as _

# https://github.com/jedie/django-tools
from django_tools.mail.settings import *
from django_tools.unittest_utils.logging_utils import CutPathnameLogRecordFactory, FilterAndLogWarnings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True

SECRET_KEY = "Unittests"
ALLOWED_HOSTS = ["*"] # Allow any domain/subdomain


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, "..", "test_project_db.sqlite3"),
        # 'NAME': ":memory:"
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

MIDDLEWARE_CLASSES = (
    # https://github.com/jazzband/django-debug-toolbar/
    'debug_toolbar.middleware.DebugToolbarMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    # 'django_tools.dynamic_site.middleware.DynamicSiteMiddleware',
    'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware',
    'django_tools.middlewares.TracebackLogMiddleware.TracebackLogMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'django.contrib.flatpages',

    'easy_thumbnails', 'filer', # for django_tools.unittest_utils.mockup

    # TODO:
    # # https://pypi.org/project/django-parler
    # 'parler',
    #
    # # https://pypi.org/project/django-ya-model-publisher/
    # 'publisher',

    'django_tools',
    'django_tools.local_sync_cache',
    # 'django_tools.dynamic_site',
    'django_tools_test_project.django_tools_test_app',

    'django_tools.manage_commands.django_tools_list_models',

    'django_tools.manage_commands.django_tools_nice_diffsettings',
)




TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates/"),
        ],
        'OPTIONS': {
            'loaders': [
                ("django_tools.template.loader.DebugCacheLoader", (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                )),
            ],
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'django.template.context_processors.static',
            ],
        },
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

# Default and fallback language:
# https://docs.djangoproject.com/en/1.11/ref/settings/#language-code
LANGUAGE_CODE = "en"

# http://django-parler.readthedocs.org/en/latest/quickstart.html#configuration
PARLER_LANGUAGES = {
    1: [
        {
            "name": _("German"),
            "code": "de",
            "fallbacks": [LANGUAGE_CODE],
            "hide_untranslated": False,
        },
        {
            "name": _("English"),
            "code": "en",
            "fallbacks": ["de"],
            "hide_untranslated": False,
        },
    ],
    "default": { # all SITE_ID"s
        "fallbacks": [LANGUAGE_CODE],
        "redirect_on_fallback": False,
    },
}


# https://docs.djangoproject.com/en/1.8/ref/settings/#languages
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGES = tuple([(d["code"], d["name"]) for d in PARLER_LANGUAGES[1]])

LANGUAGE_DICT = dict(LANGUAGES) # useful to get translated name by language code

# http://docs.django-cms.org/en/latest/reference/configuration.html#std:setting-CMS_LANGUAGES
# CMS_LANGUAGES = PARLER_LANGUAGES

# http://django-parler.readthedocs.org/en/latest/quickstart.html#configuration
PARLER_DEFAULT_LANGUAGE_CODE = LANGUAGE_CODE


#==============================================================================

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_always_eager
CELERY_TASK_ALWAYS_EAGER = True  # Celery tasks doesn't use a queue

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True # executed tasks will propagate exceptions

EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'

#==============================================================================

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#==============================================================================


SITE_ID = 1

USE_DYNAMIC_SITE_MIDDLEWARE = True

ROOT_URLCONF = 'django_tools_test_project.django_tools_test_app.urls'

PASSWORD_HASHERS = ( # Speedup tests
    'django.contrib.auth.hashers.MD5PasswordHasher',
)


#_____________________________________________________________________________

# Adds 'cut_path' attribute on log record. So '%(cut_path)s' can be used in log formatter.
# django_tools.unittest_utils.logging_utils.CutPathnameLogRecordFactory
logging.setLogRecordFactory(CutPathnameLogRecordFactory(max_length=50))

# Filter warnings and pipe them to logging system:
# django_tools.unittest_utils.logging_utils.FilterAndLogWarnings
warnings.showwarning = FilterAndLogWarnings()

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
                # 'null',
                'console'
            ],
            'level': 'DEBUG',
        },
        "django_tools.DynamicSite": {
            'handlers': [
                # 'null',
                'console'
            ],
            'level': 'DEBUG',
        },
    },
}
