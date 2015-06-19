import time
from importlib import import_module
from io import BytesIO

from django.apps import apps
from django.conf import settings
from django.http import HttpResponse
from django.http import SimpleCookie


class FakedHttpResponse(HttpResponse):
    """
    Used in selenium tests.
    So django assert statements like
    assertContains() can be used.
    """
    pass


def selenium2fakes_response(driver, client, client_class):
    """
    Create a similar 'testing-response' [1] here.
    So that some of the django testing assertions [2] can be used
    with selenium tests, too ;)

    [1] https://docs.djangoproject.com/en/1.7/topics/testing/tools/#testing-responses
    [2] https://docs.djangoproject.com/en/1.7/topics/testing/tools/#assertions

    Currently not available:
        * response.status_code
        * response.redirect_chain
        * response.templates
        * response.context

    Available:
        * response.content
        * response.cookies
        * response.client.cookies
        * response.session

    usage e.g.:
        from django_tools.unittest_utils.selenium_utils import selenium2fakes_response

        class MySeleniumTests(StaticLiveServerTestCase):
            def get_faked_response(self):
                return selenium2fakes_response(self.driver, self.client, self.client_class)
            def test_foo(self):
                self.driver.get("/foo")
                faked_response = self.get_faked_response()
                self.assertNotContains(response, "<h1>foobar</h1>", html=True)
    """
    response = FakedHttpResponse(content=driver.page_source)
    response.client = client_class() # Fresh Client() instance

    # Add 'response.client.cookies':
    # driver.get_cookies() is a simple list of dict items, e.g.:
    # [{'name': 'csrftoken', 'value': 'yXoN3...', ...},...]
    cookies = SimpleCookie()
    for cookie in driver.get_cookies():
        key = cookie.pop("name")
        cookies[key] = cookie.pop("value")
        for k, v in cookie.items():
            if k == "expiry":
                cookies[key]["expires"] = time.time() - v
            else:
                cookies[key][k] = v

    # response.cookies and response.client.cookies
    response.cookies = response.client.cookies = cookies
    # print("\nresponse.cookies:", response.cookies)

    # Add 'response.session':
    response.session = response.client.session
    # print("\nresponse.session:", dict(response.session))

    return response
