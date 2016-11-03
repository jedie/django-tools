# encoding: utf-8


import unittest

from django.utils.six import PY2, binary_type

from django_tools.utils import http



class HttpTests(unittest.TestCase):
    def test_http_request(self):
        r = http.HttpRequest("http://www.google.com", timeout=3, threadunsafe_workaround=True)
        response = r.get_response()

        # print("-"*79)
        # print("repr(request_header):")
        # print(repr(response.request_header))
        # print("-"*79)
        # print("response.info():")
        # print(response.info())
        # print("-"*79)

        if PY2:
            self.assertIn("Host: www.google.", response.request_header)
        else:
            self.assertIn(b"Host: www.google.", response.request_header)

        response_info = response.info()
        self.assertEqual(response_info.get("Server"), "gws")
        self.assertEqual(response_info["content-type"], "text/html; charset=ISO-8859-1")

        self.assertEqual(response.getcode(), 200)

        content = r.get_unicode()
        self.assertIn("google.com", content)
        self.assertIn("https", content)

    @unittest.skipIf(not http.HTTPS_SUPPORT, "no https support :(")
    def test_https_request(self):
        r = http.HttpRequest("https://www.google.com", timeout=3, threadunsafe_workaround=True)
        response = r.get_response()
        url = response.geturl()
        self.assertIn("https://www.google.", url)
