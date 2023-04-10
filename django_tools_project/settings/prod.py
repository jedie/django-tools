"""
    Base Django settings
"""

import logging
from pathlib import Path as __Path

from bx_py_utils.path import assert_is_dir
from django.utils.translation import gettext_lazy as _


###############################################################################

# Build paths relative to the project root:
BASE_PATH = __Path(__file__).parent.parent.parent
print(f'BASE_PATH:{BASE_PATH}')
assert_is_dir(BASE_PATH / 'django_tools_project')

###############################################################################


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Serve static/media files by Django?
# In production the Webserver should serve this!
SERVE_FILES = False


# SECURITY WARNING: keep the secret key used in production secret!
__SECRET_FILE = __Path(BASE_PATH, 'secret.txt').resolve()
if not __SECRET_FILE.is_file():
    print(f'Generate {__SECRET_FILE}')
    from secrets import token_urlsafe as __token_urlsafe

    __SECRET_FILE.write_text(__token_urlsafe(128))

SECRET_KEY = __SECRET_FILE.read_text().strip()


# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.staticfiles",
    "django.contrib.admindocs",
    "django.contrib.flatpages",
    "django.contrib.messages",
    # TODO:
    # # https://pypi.org/project/django-parler
    # 'parler',
    #
    # # https://pypi.org/project/django-ya-model-publisher/
    # 'publisher',
    "django_tools.local_sync_cache",
    "django_tools_project.django_tools_test_app",
    'django_tools.serve_media_app.apps.UserMediaFilesConfig',
    'django_tools.model_version_protect.apps.ModelVersionProtectConfig',
    'django_tools.apps.AppConfig',
]

SITE_ID = 1

USE_DYNAMIC_SITE_MIDDLEWARE = True

ROOT_URLCONF = 'django_tools_project.urls'
WSGI_APPLICATION = 'django_tools_project.wsgi.application'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    "django_tools.middlewares.LogHeaders.LogRequestHeadersMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware",
    "django_tools.middlewares.TracebackLogMiddleware.TracebackLogMiddleware",
]

__TEMPLATE_DIR = __Path(BASE_PATH, 'django_tools', 'templates')
assert_is_dir(__TEMPLATE_DIR)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [str(__TEMPLATE_DIR)],
        'OPTIONS': {
            'loaders': [
                (
                    'django_tools.template.loader.DebugCacheLoader',
                    ('django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader'),
                )
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
                'django_tools.context_processors.django_tools_version_string',
            ],
        },
    },
]


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# _____________________________________________________________________________
# Internationalization

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
]
USE_I18N = True
TIME_ZONE = 'Europe/Paris'
USE_TZ = True

# _____________________________________________________________________________
# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = str(__Path(BASE_PATH, 'static'))

MEDIA_URL = '/media/'
MEDIA_ROOT = str(__Path(BASE_PATH, 'media'))


# _____________________________________________________________________________
# Cache Backend

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}


# _____________________________________________________________________________
# cut 'pathname' in log output

old_factory = logging.getLogRecordFactory()


def cut_path(pathname, max_length):
    if len(pathname) <= max_length:
        return pathname
    return f'...{pathname[-(max_length - 3):]}'


def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.cut_path = cut_path(record.pathname, 30)
    return record


logging.setLogRecordFactory(record_factory)

# -----------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'colored': {  # https://github.com/borntyping/python-colorlog
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(asctime)s %(levelname)8s %(cut_path)s:%(lineno)-3s %(message)s',
        }
    },
    'handlers': {'console': {'class': 'colorlog.StreamHandler', 'formatter': 'colored'}},
    'loggers': {
        '': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'django_tools': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}
