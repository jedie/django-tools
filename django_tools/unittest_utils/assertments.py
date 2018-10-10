"""
    :created: 28.08.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pathlib import Path

from django.conf import settings
from django.core import mail
from django.core.mail import get_connection


def assert_startswith(text, prefix):
    """
    Check if test starts with prefix.
    """
    assert text.startswith(prefix), "%r doesn't starts with %r" % (text, prefix)


def assert_endswith(text, suffix):
    """
    Check if text ends with suffix.
    """
    assert text.endswith(suffix), "%r doesn't ends with %r" % (text, suffix)


def assert_locmem_mail_backend():
    """
    Check if current email backend is the In-memory backend.
    See:
        https://docs.djangoproject.com/en/1.11/topics/email/#in-memory-backend
    """
    mail_backend = get_connection()
    assert isinstance(mail_backend, mail.backends.locmem.EmailBackend), "Wrong backend: %s" % mail_backend


def assert_language_code(*, language_code):
    """
    Check if given language_code is in settings.LANGUAGES
    """
    existing_language_codes = tuple(dict(settings.LANGUAGES).keys())
    assert language_code in existing_language_codes, "%r not in settings.LANGUAGES=%r" % (
        language_code,
        settings.LANGUAGES,
    )


def assert_installed_apps(*, app_names):
    """
    Check entries in settings.INSTALLED_APPS
    """
    assert isinstance(app_names, (tuple, list))
    installed_apps = settings.INSTALLED_APPS
    for app_name in app_names:
        assert app_name in installed_apps, "%r not in settings.INSTALLED_APPS!" % app_name


def assert_is_dir(path):
    """
    Check if given path is a directory
    """
    if not isinstance(path, Path):
        path = Path(path)
    assert path.is_dir(), "Directory not exists: %s" % path


def assert_is_file(path):
    """
    Check if given path is a file
    """
    if not isinstance(path, Path):
        path = Path(path)
    assert_is_dir(path.parent)
    assert path.is_file(), "File not exists: %s" % path


def assert_path_not_exists(path):
    """
    Check if given path doesn't exists
    """
    if not isinstance(path, Path):
        path = Path(path)

    assert not path.is_dir(), "Path is a existing directory: %s" % path
    assert not path.is_file(), "Path is a existing file: %s" % path
    assert not path.is_fifo(), "Path is a existing fifo: %s" % path
    assert not path.exists(), "Path exists: %s" % path
