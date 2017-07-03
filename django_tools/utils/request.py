# coding:utf-8

"""
    :copyleft: 2017 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, absolute_import, print_function

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory


def create_fake_request(url="/", session=None, language_code=None, user=None, **extra):
    if session is None:
        session = {}

    if language_code is None:
        language_code = settings.LANGUAGE_CODE

    if user is None:
        user = AnonymousUser()

    fake_request = RequestFactory().get(url)

    fake_request.session = session
    fake_request.LANGUAGE_CODE = language_code
    fake_request.user = user

    for key, value in extra.items():
        setattr(fake_request, key, value)

    return fake_request
