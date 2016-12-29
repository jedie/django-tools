
import logging

from django.test import TestCase

from django_tools.unittest_utils.logging_utils import LoggingBuffer


class TestTracebackLogMiddleware(TestCase):
    def test_exception_logging(self):
        with LoggingBuffer(name=None, level=logging.ERROR) as log:
            with self.assertRaises(Exception):
                self.client.get('/raise_exception/TestTracebackLogMiddleware/')

        self.assertIn(
            "Exception on url: /raise_exception/TestTracebackLogMiddleware/",
            log.get_messages()
        )
        self.assertIn(
            "Traceback (most recent call last):",
            log.get_messages()
        )
        self.assertIn(
            'django_tools_test_app/views.py", line 41, in raise_exception',
            log.get_messages()
        )
        self.assertIn(
            "Exception: TestTracebackLogMiddleware",
            log.get_messages()
        )
