"""
    :created: 21.08.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging
import time
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.test import RequestFactory, SimpleTestCase, override_settings

# https://github.com/jedie/django-tools
from django_tools.debug.delay import CacheDelay
from django_tools.unittest_utils.logging_utils import LoggingBuffer
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import TestUserMixin


class CacheDelayTests(SimpleTestCase):

    def setUp(self):
        super().setUp()
        cache.clear()

    def _get_request(self, url):
        rf = RequestFactory()
        request = rf.get(url)
        request.user = AnonymousUser()
        return request

    def test_delay(self):
        request = self._get_request("/foo/bar/?delay=2")

        with LoggingBuffer(name="django_tools.debug.delay", level=logging.DEBUG) as log:
            CacheDelay(
                key="delay", only_debug=False
            ).load(
                request,
                query_string="delay",
            )

        log.assert_messages([
            "INFO:django_tools.debug.delay:Add 'delay' value to cache",
            "WARNING:django_tools.debug.delay:Save 2 sec. from 'delay' for 'delay' into cache"
        ])

        with LoggingBuffer(name="django_tools.debug.delay", level=logging.DEBUG) as log:
            with mock.patch.object(time, 'sleep', return_value=None) as mock_method:
                CacheDelay(key="delay", only_debug=False).sleep()

        log.assert_messages(["WARNING:django_tools.debug.delay:Delay 2 sec. for 'delay'"])

        mock_method.assert_called_once_with(2)

    def test_not_set(self):
        with LoggingBuffer(name="django_tools.debug.delay", level=logging.DEBUG) as log:
            with mock.patch.object(time, 'sleep', return_value=None) as mock_method:
                CacheDelay(key="test_not_set", only_debug=False).sleep()

        log.assert_messages(["DEBUG:django_tools.debug.delay:No delay for 'test_not_set' from cache"])

        mock_method.assert_not_called()

    @override_settings(DEBUG=False)
    def test_only_debug(self):
        request = self._get_request("/foo/bar/?delay=2")

        with LoggingBuffer(name="django_tools.debug.delay", level=logging.DEBUG) as log:
            CacheDelay(key="delay").load(
                request,
                query_string="delay",
            )

        log.assert_messages(["DEBUG:django_tools.debug.delay:Ignore ?delay, because DEBUG is not ON!"])

    def test_default_value(self):
        request = self._get_request("/foo/bar/?test_default_value")

        with LoggingBuffer(name="django_tools.debug.delay", level=logging.DEBUG) as log:
            CacheDelay(
                key="delay", only_debug=False
            ).load(
                request,
                query_string="test_default_value",
                default=123,
            )

        log.assert_messages([
            "INFO:django_tools.debug.delay:Add 'test_default_value' value to cache",
            "WARNING:django_tools.debug.delay:Save 123 sec. from 'test_default_value' for 'delay' into cache"
        ])

        with LoggingBuffer(name="django_tools.debug.delay", level=logging.DEBUG) as log:
            with mock.patch.object(time, 'sleep', return_value=None) as mock_method:
                CacheDelay(key="delay", only_debug=False).sleep()

        log.assert_messages(["WARNING:django_tools.debug.delay:Delay 123 sec. for 'delay'"])

        mock_method.assert_called_once_with(123)

    def test_delete_value(self):
        request = self._get_request("/foo/bar/?test_delete_value=3")

        with LoggingBuffer(name="django_tools.debug.delay", level=logging.DEBUG) as log:
            CacheDelay(
                key="delay", only_debug=False
            ).load(
                request,
                query_string="test_delete_value",
            )

        log.assert_messages([
            "INFO:django_tools.debug.delay:Add 'test_delete_value' value to cache",
            "WARNING:django_tools.debug.delay:Save 3 sec. from 'test_delete_value' for 'delay' into cache"
        ])

        with LoggingBuffer(name="django_tools.debug.delay", level=logging.DEBUG) as log:
            CacheDelay(
                key="delay", only_debug=False
            ).load(
                request,
                query_string="not_existing_key",
            )

        log.assert_messages(["DEBUG:django_tools.debug.delay:Delete 'delay' delay from cache"])


class SessionDelayTests(TestUserMixin, BaseTestCase):

    def setUp(self):
        super().setUp()
        self.client.logout()

    def test_delay(self):

        with LoggingBuffer(name="django_tools.debug.delay", level=logging.DEBUG) as log:
            with mock.patch.object(time, 'sleep', return_value=None) as mock_method:
                response = self.client.get("/delay/?sec=0.02")

        self.assertResponse(
            response,
            must_contain=("django_tools_test_project.django_tools_test_app.views.delay_view",),
            must_not_contain=("error", "traceback"),
            status_code=200,
            messages=[],
            html=False,
            browser_traceback=True
        )

        log.assert_messages([
            "INFO:django_tools.debug.delay:Add 'sec' value to session",
            "WARNING:django_tools.debug.delay:Save 0.02 sec. from 'sec' for 'delay_view' into session",
            "WARNING:django_tools.debug.delay:Delay 0.02 sec. for 'delay_view'"
        ])

        mock_method.assert_called_once_with(0.02)

    def test_not_set(self):
        with LoggingBuffer(name="django_tools.debug.delay", level=logging.DEBUG) as log:
            with mock.patch.object(time, 'sleep', return_value=None) as mock_method:
                response = self.client.get("/delay/")

        self.assertResponse(
            response,
            must_contain=("django_tools_test_project.django_tools_test_app.views.delay_view",),
            must_not_contain=("error", "traceback"),
            status_code=200,
            messages=[],
            html=False,
            browser_traceback=True
        )

        log.assert_messages(["DEBUG:django_tools.debug.delay:No delay for 'delay_view' from session"])

        mock_method.assert_not_called()

    def test_message(self):
        self.login(usertype="normal")
        with mock.patch.object(time, 'sleep', return_value=None) as mock_method:
            response = self.client.get("/delay/?sec=3")

        self.assertResponse(
            response,
            must_contain=("django_tools_test_project.django_tools_test_app.views.delay_view",),
            must_not_contain=("error", "traceback"),
            status_code=200,
            messages=["Use 3 sec. 'sec'"],
            html=False,
            browser_traceback=True
        )
