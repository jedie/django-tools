# coding: utf-8

from __future__ import absolute_import, division, print_function

import logging

from django.test import TestCase

from django_tools.unittest_utils.logging_utils import LoggingBuffer


class TestTracebackLogMiddleware(TestCase):
    def test_exception_logging(self):
        with LoggingBuffer(name=None, level=logging.ERROR) as log:
            with self.assertRaises(Exception):
                self.client.get('/raise_exception/TestTracebackLogMiddleware/')

        messages = log.get_messages()
        print(messages)

        self.assertIn(
            "Exception on url: /raise_exception/TestTracebackLogMiddleware/",
            messages
        )
        self.assertIn(
            "Traceback (most recent call last):",
            messages
        )
        self.assertIn(
            'django_tools_test_app/views.py", line ',
            messages
        )
        self.assertIn(
            'in raise_exception',
            messages
        )
        self.assertIn(
            'raise Exception(msg)',
            messages
        )
        self.assertIn(
            "Exception: TestTracebackLogMiddleware",
            messages
        )
