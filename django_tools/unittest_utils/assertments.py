"""
    :created: 28.08.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.core import mail
from django.core.mail import get_connection


def assert_startswith(text, prefix):
    assert text.startswith(prefix), "%r doesn't starts with %r" % (text, prefix)


def assert_endswith(text, suffix):
    assert text.endswith(suffix), "%r doesn't ends with %r" % (text, suffix)


def assert_locmem_mail_backend():
    """
    Check if current email backend is the In-memory backend
    See:
        https://docs.djangoproject.com/en/1.11/topics/email/#in-memory-backend
    """
    mail_backend = get_connection()
    assert isinstance(mail_backend, mail.backends.locmem.EmailBackend), "Wrong backend: %s" % mail_backend
