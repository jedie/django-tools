
"""
    :created: 06.04.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import logging
import warnings

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.logging_utils import FilterAndLogWarnings, LoggingBuffer
from django_tools.unittest_utils.unittest_base import BaseUnittestCase

log = logging.getLogger(__name__)


class TestLoggingUtilsTestCase(BaseUnittestCase):

    def test_filter_and_log_warnings_create_warning(self):
        with LoggingBuffer(name=None, level=logging.DEBUG) as log_buffer:
            warnings.warn("test_filter_and_log_warnings_create_warning", UserWarning)

        self.assertEqual(
            log_buffer.get_messages(),
            "WARNING:django_tools.unittest_utils.logging_utils:UserWarning:test_filter_and_log_warnings_create_warning"
        )

    def test_filter_and_log_warnings_direct_call(self):
        instance = FilterAndLogWarnings()
        with LoggingBuffer(name=None, level=logging.DEBUG) as log_buffer:
            instance(
                message="test_filter_and_log_warnings_direct_call",
                category=UserWarning,
                filename="/foo/bar.py",
                lineno=123
            )

        self.assertEqual(
            log_buffer.get_messages(),
            "WARNING:django_tools.unittest_utils.logging_utils:UserWarning:test_filter_and_log_warnings_direct_call"
        )

    def test_filter_and_log_skip_external_package(self):
        instance = FilterAndLogWarnings()
        with LoggingBuffer(name=None, level=logging.DEBUG) as log_buffer:
            for i in range(3):
                instance(
                    message="test_filter_and_log_skip_external_package dist-packages %i" % i,
                    category=UserWarning,
                    filename="/foo/dist-packages/bar.py",
                    lineno=456
                )
                instance(
                    message="test_filter_and_log_skip_external_package site-packages %i" % i,
                    category=UserWarning,
                    filename="/foo/site-packages/bar.py",
                    lineno=789
                )

        log_messages = log_buffer.get_messages()
        print("log_messages:\n%s" % log_messages)

        self.assertEqual(
            log_messages,
            (
                "WARNING:django_tools.unittest_utils.logging_utils:There are warnings in: /foo/dist-packages/bar.py\n"
                "WARNING:django_tools.unittest_utils.logging_utils:There are warnings in: /foo/site-packages/bar.py"
            )
        )
