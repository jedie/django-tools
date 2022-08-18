import logging
import warnings
from pathlib import Path as __Path

from django.utils.translation import gettext_lazy as _

from django_tools.unittest_utils.logging_utils import (
    CutPathnameLogRecordFactory,
    FilterAndLogWarnings,
)


###############################################################################

# Build paths relative to the project root:
BASE_PATH = __Path(__file__).parent.parent.parent
print(f'BASE_PATH:{BASE_PATH}')
assert __Path(BASE_PATH, 'django_tools').is_dir()

###############################################################################

DEBUG = True

SECRET_KEY = "Unittests"
ALLOWED_HOSTS = ["*"]  # Allow any domain/subdomain

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_PATH / "test_project_db.sqlite3"),
        # 'NAME': ":memory:",
        'OPTIONS': {
            # https://docs.djangoproject.com/en/2.2/ref/databases/#database-is-locked-errors
            'timeout': 20,
        }
    }
}
print(f'Test DB: {DATABASES["default"]["NAME"]}')

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}


MIDDLEWARE = (
    "django_tools.middlewares.LogHeaders.LogRequestHeadersMiddleware",
    # https://github.com/jazzband/django-debug-toolbar/
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # 'django_tools.dynamic_site.middleware.DynamicSiteMiddleware',
    "django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware",
    "django_tools.middlewares.TracebackLogMiddleware.TracebackLogMiddleware",
)

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.staticfiles",
    "django.contrib.admindocs",
    "django.contrib.flatpages",
    "django.contrib.messages",
    "easy_thumbnails",
    "filer",  # for django_tools.unittest_utils.mockup
    # TODO:
    # # https://pypi.org/project/django-parler
    # 'parler',
    #
    # # https://pypi.org/project/django-ya-model-publisher/
    # 'publisher',
    "django_tools.apps.DjangoToolsConfig",
    "django_tools.local_sync_cache",
    "django_tools_test_project.django_tools_test_app",
    'django_tools.serve_media_app.apps.UserMediaFilesConfig',
    'django_tools.model_version_protect.apps.ModelVersionProtectConfig',
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(__Path(BASE_PATH, 'django_tools', 'templates'))],
        "OPTIONS": {
            "loaders": [
                (
                    "django_tools.template.loader.DebugCacheLoader",
                    (
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader"
                    ),
                )
            ],
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.template.context_processors.csrf",
                "django.template.context_processors.tz",
                "django.template.context_processors.static",
            ],
        },
    }
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
        {"name": _("English"), "code": "en", "fallbacks": ["de"], "hide_untranslated": False},
    ],
    "default": {"fallbacks": [LANGUAGE_CODE], "redirect_on_fallback": False},  # all SITE_ID"s
}

# https://docs.djangoproject.com/en/1.8/ref/settings/#languages
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGES = tuple((d["code"], d["name"]) for d in PARLER_LANGUAGES[1])

LANGUAGE_DICT = dict(LANGUAGES)  # useful to get translated name by language code

# http://docs.django-cms.org/en/latest/reference/configuration.html#std:setting-CMS_LANGUAGES
# CMS_LANGUAGES = PARLER_LANGUAGES

# http://django-parler.readthedocs.org/en/latest/quickstart.html#configuration
PARLER_DEFAULT_LANGUAGE_CODE = LANGUAGE_CODE

# ==============================================================================

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# ==============================================================================

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = __Path(BASE_PATH, 'static')
STATIC_ROOT.mkdir(exist_ok=True)
STATIC_ROOT = str(STATIC_ROOT)

MEDIA_URL = '/media/'
MEDIA_ROOT = __Path(BASE_PATH, 'media')
MEDIA_ROOT.mkdir(exist_ok=True)
MEDIA_ROOT = str(MEDIA_ROOT)

# ==============================================================================

SITE_ID = 1

USE_DYNAMIC_SITE_MIDDLEWARE = True

ROOT_URLCONF = "django_tools_test_project.urls"

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)  # Speedup tests

# _____________________________________________________________________________

# Adds 'cut_path' attribute on log record. So '%(cut_path)s' can be used in log formatter.
# django_tools.unittest_utils.logging_utils.CutPathnameLogRecordFactory
logging.setLogRecordFactory(CutPathnameLogRecordFactory(max_length=50))

# Filter warnings and pipe them to logging system:
# django_tools.unittest_utils.logging_utils.FilterAndLogWarnings
warnings.showwarning = FilterAndLogWarnings()

# -----------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "colored": {  # https://github.com/borntyping/python-colorlog
            "()": "colorlog.ColoredFormatter",
            #
            # https://docs.python.org/3/library/logging.html#logrecord-attributes
            "format": "%(log_color)s%(asctime)s %(levelname)8s %(cut_path)s:%(lineno)-3s %(name)s %(message)s",
        }
    },
    "handlers": {"console": {"class": "colorlog.StreamHandler", "formatter": "colored"}},
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "django_tools": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "django_tools.DynamicSite": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}
