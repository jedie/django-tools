import warnings

from django.test import SimpleTestCase
from django.test.client import RequestFactory
from django.http import HttpResponse


from django_tools.utils.client_storage import SignedCookieStorage, SignedCookieStorageError, ClientCookieStorage



class TestSignedCookieStorage(SimpleTestCase):
    def test_signed_cookie1(self):

        response = HttpResponse("example")

        c = SignedCookieStorage("foo", max_age=123)
        response = c.save_data("bar", response)
        cookie = response.cookies["foo"]

        cookie_value = cookie.value
        # print(cookie_value) # e.g.: ImJhciI:1Z1xMG:XtRHzUuEg4xfiJPl-QeIbpWS3jM

        self.assertNotIn("bar", cookie_value)
        self.assertNotIn("foo", cookie_value)
        self.assertEqual(cookie["max-age"], 123)

        # print(response.cookies) # e.g.: Set-Cookie: foo=ImJhciI:1Z1y0f:wA2m4wjbUEwkS6TxK7gqZV9yk7M; expires=...
        self.assertIn("foo", response.cookies)

        request = RequestFactory().get('/', HTTP_COOKIE="foo=%s" % cookie_value)
        c = SignedCookieStorage("foo", max_age=123)
        self.assertEqual(c.get_data(request), "bar")

        # Try to access a not existing cookie:
        c = SignedCookieStorage("wrong name")
        self.assertRaises(SignedCookieStorageError, c.get_data, request)
        try:
            c.get_data(request)
        except SignedCookieStorageError as err:
            self.assertEqual(str(err), "Cookie 'wrong name' doesn't exists")

        # The existing, still there:
        c = SignedCookieStorage("foo", max_age=123)
        self.assertEqual(c.get_data(request), "bar")
    
    def test_wrong_data(self):
        request = RequestFactory().get('/', HTTP_COOKIE="foo=value:timestamp:wrong_dataABCDEFGHIJKLMNOPQ")
        c = SignedCookieStorage("foo")

        self.assertRaises(SignedCookieStorageError, c.get_data, request)
        try:
            c.get_data(request)
        except SignedCookieStorageError as err:
            self.assertEqual(str(err), """Can't load data: Signature "wrong_dataABCDEFGHIJKLMNOPQ" does not match""")

    def test_old_api(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always") # trigger all warnings

            c = ClientCookieStorage(cookie_key="foo")

            self.assertEqual(len(w), 1)
            self.assertEqual(str(w[-1].message), "ClientCookieStorage is old API! Please change to SignedCookieStorage! This will be removed in the future!")
            # self.assertIsInstance(w[-1].category, FutureWarning) # FIXME: AssertionError: <class 'FutureWarning'> is not an instance of <class 'FutureWarning'>
            self.assertTrue(issubclass(w[-1].category, FutureWarning))




