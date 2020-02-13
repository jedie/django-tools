"""
    :copyleft: 2017-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.utils.request import create_fake_request


class TestRequestUtils(unittest.TestCase):
    def test_defaults(self):
        fake_request = create_fake_request()
        self.assertIsInstance(fake_request, WSGIRequest)

        assert_pformat_equal(fake_request.path, "/")
        assert_pformat_equal(fake_request.session, {})
        assert_pformat_equal(fake_request.LANGUAGE_CODE, settings.LANGUAGE_CODE)
        self.assertIsInstance(fake_request.user, AnonymousUser)

    def test_change_defaults(self):
        class MockUser:
            pass

        mock_user = MockUser()

        fake_request = create_fake_request(
            url="/foo/bar",
            session={"foo": "bar"},
            language_code="es",
            user=mock_user,
            extra_attr1=True,
            extra_attr2=1234,
        )
        self.assertIsInstance(fake_request, WSGIRequest)

        assert_pformat_equal(fake_request.path, "/foo/bar")
        assert_pformat_equal(fake_request.session, {"foo": "bar"})
        assert_pformat_equal(fake_request.LANGUAGE_CODE, "es")
        assert_pformat_equal(fake_request.user, mock_user)
        assert_pformat_equal(fake_request.extra_attr1, True)
        assert_pformat_equal(fake_request.extra_attr2, 1234)
