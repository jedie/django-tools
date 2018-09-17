"""
    :created: 28.08.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
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
        language_code, settings.LANGUAGES
    )
