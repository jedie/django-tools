"""
    :copyleft: 2017-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import json

from django.test import TestCase

# https://github.com/jedie/django-tools
from django_tools.middlewares.ThreadLocal import get_current_request
from django_tools.unittest_utils.assertments import assert_pformat_equal


class TestGetCurrentRequest(TestCase):
    def test_current_request_receives_current_request(self):
        response = self.client.get("/get_current_get_parameters/?")
        current_get_parameters = json.loads(response.content.decode("utf-8"))
        assert_pformat_equal(current_get_parameters, {})
        response = self.client.get("/get_current_get_parameters/?foo=bar")
        current_get_parameters = json.loads(response.content.decode("utf-8"))
        assert_pformat_equal(current_get_parameters, {"foo": "bar"})

    def test_current_request_is_cleared_after_request_is_finished(self):
        self.client.get("/get_current_get_parameters/")
        assert_pformat_equal(get_current_request(), None)

    def test_current_request_is_cleared_when_exception_is_raised(self):
        with self.assertRaises(Exception):
            self.client.get("/raise_exception/TestGetCurrentRequest/")
        assert_pformat_equal(get_current_request(), None)
