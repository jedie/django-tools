# coding: utf-8

from __future__ import unicode_literals

import unittest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest

from django_tools.utils.request import create_fake_request


class TestRequestUtils(unittest.TestCase):
    def test_defaults(self):
        fake_request = create_fake_request()
        self.assertIsInstance(fake_request, WSGIRequest)

        self.assertEqual(fake_request.path, "/")
        self.assertEqual(fake_request.session, {})
        self.assertEqual(fake_request.LANGUAGE_CODE, settings.LANGUAGE_CODE)
        self.assertIsInstance(fake_request.user, AnonymousUser)

    def test_change_defaults(self):
        class MockUser(object):
            pass
        mock_user = MockUser()

        fake_request = create_fake_request(
            url="/foo/bar",
            session={"foo":"bar"},
            language_code="es",
            user=mock_user,
            extra_attr1=True,
            extra_attr2=1234
        )
        self.assertIsInstance(fake_request, WSGIRequest)

        self.assertEqual(fake_request.path, "/foo/bar")
        self.assertEqual(fake_request.session, {"foo":"bar"})
        self.assertEqual(fake_request.LANGUAGE_CODE, "es")
        self.assertEqual(fake_request.user, mock_user)
        self.assertEqual(fake_request.extra_attr1, True)
        self.assertEqual(fake_request.extra_attr2, 1234)

