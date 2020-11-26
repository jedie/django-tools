import logging

from django_tools.unittest_utils.logging_utils import FilterAndLogWarnings
from django_tools.unittest_utils.unittest_base import BaseUnittestCase


log = logging.getLogger(__name__)


class TestLoggingUtilsTestCase(BaseUnittestCase):

    def test_filter_and_log_warnings_direct_call(self):
        instance = FilterAndLogWarnings()
        with self.assertLogs(logger="django_tools.unittest_utils.logging_utils", level=logging.DEBUG) as logs:
            instance(
                message="test_filter_and_log_warnings_direct_call",
                category=UserWarning,
                filename="/foo/bar.py",
                lineno=123,
            )

        assert logs.output == [
            "WARNING:django_tools.unittest_utils.logging_utils:UserWarning:test_filter_and_log_warnings_direct_call",
        ]

    def test_filter_and_log_skip_external_package(self):
        instance = FilterAndLogWarnings()
        with self.assertLogs(logger="django_tools.unittest_utils.logging_utils", level=logging.DEBUG) as logs:
            for i in range(3):
                instance(
                    message=f"test_filter_and_log_skip_external_package dist-packages {i:d}",
                    category=UserWarning,
                    filename="/foo/dist-packages/bar.py",
                    lineno=456,
                )
                instance(
                    message=f"test_filter_and_log_skip_external_package site-packages {i:d}",
                    category=UserWarning,
                    filename="/foo/site-packages/bar.py",
                    lineno=789,
                )

        assert logs.output == [
            "WARNING:django_tools.unittest_utils.logging_utils:There are warnings in: /foo/dist-packages/bar.py",
            "WARNING:django_tools.unittest_utils.logging_utils:There are warnings in: /foo/site-packages/bar.py"
        ]
