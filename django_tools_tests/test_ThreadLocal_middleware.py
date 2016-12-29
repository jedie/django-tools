import json

from django.test import TestCase

from django_tools.middlewares.ThreadLocal import get_current_request


class TestGetCurrentRequest(TestCase):
    def test_current_request_receives_current_request(self):
        response = self.client.get('/get_current_get_parameters/?')
        current_get_parameters = json.loads(response.content.decode('utf-8'))
        self.assertEqual(current_get_parameters, {})
        response = self.client.get('/get_current_get_parameters/?foo=bar')
        current_get_parameters = json.loads(response.content.decode('utf-8'))
        self.assertEqual(current_get_parameters, {'foo': 'bar'})

    def test_current_request_is_cleared_after_request_is_finished(self):
        response = self.client.get('/get_current_get_parameters/')
        self.assertEqual(get_current_request(), None)

    def test_current_request_is_cleared_when_exception_is_raised(self):
        with self.assertRaises(Exception):
            response = self.client.get('/raise_exception/TestGetCurrentRequest/')
        self.assertEqual(get_current_request(), None)
