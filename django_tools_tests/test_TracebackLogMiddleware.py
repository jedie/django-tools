from django.test import TestCase


class TestTracebackLogMiddleware(TestCase):
    def test_exception_logging(self):
        with self.assertLogs(logger=None, level=None) as logs:
            with self.assertRaises(Exception):
                self.client.get('/raise_exception/TestTracebackLogMiddleware/')

        output = '\n'.join([str(entry) for entry in logs.output])

        assert 'Exception on url: /raise_exception/TestTracebackLogMiddleware/' in output
        assert 'Traceback (most recent call last):' in output
        assert 'django_tools_test_app/views.py' in output
        assert 'Exception: TestTracebackLogMiddleware' in output
