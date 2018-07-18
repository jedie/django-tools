"""
    :created: 2015 by Jens Diemer
    :copyleft: 2015-2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging
import os
import sys
import time
import traceback
import warnings
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.http import HttpResponse, SimpleCookie
from django.test import RequestFactory, TestCase

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

log = logging.getLogger(__name__)


class FakedHttpResponse(HttpResponse):
    """
    Used in selenium tests.
    So django assert statements like
    assertContains() can be used.
    """
    pass


def selenium2faked_response(driver, client, client_class):
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
        from django_tools.unittest_utils.selenium_utils import selenium2faked_response

        class MySeleniumTests(StaticLiveServerTestCase):
            def get_faked_response(self):
                return selenium2faked_response(self.driver, self.client, self.client_class)
            def test_foo(self):
                self.driver.get("/foo")
                faked_response = self.get_faked_response()
                self.assertNotContains(response, "<h1>foobar</h1>", html=True)
    """
    response = FakedHttpResponse(content=driver.page_source)
    response.client = client_class()  # Fresh Client() instance

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

    help(driver)

    response.request = RequestFactory()
    response.request.path = driver.current_url

    return response


def selenium2fakes_response(*args, **kwargs):
    warnings.warn(
        "selenium2fakes_response() is deprecated, use selenium2faked_response() !", category=DeprecationWarning
    )
    return selenium2faked_response(*args, **kwargs)


class SeleniumBaseTestCase(TestCase, StaticLiveServerTestCase):
    """
    inherit only from 'LiveServerTestCase' will result in
    a empty database after test run.

    See:

    https://github.com/pytest-dev/pytest-django/issues/613
    https://code.djangoproject.com/ticket/25251
    https://github.com/django/django/pull/7528
    """

    @classmethod
    def tearDownClass(cls):
        if cls.driver is not None:
            cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        if self.driver is not None:
            self.driver.delete_all_cookies()

    def _wait(self, conditions, timeout=5, msg="wait timeout"):
        """
        Wait for the given condition.
        Display page_source on error.
        """
        try:
            check = WebDriverWait(self.driver, timeout).until(conditions)
        except TimeoutException as err:
            print("\nError: %s\n%s\npage source:\n%s\n" % (msg, err, self.driver.page_source))
            raise
        else:
            self.assertTrue(check)

    def get_faked_response(self):
        """
        Create a similar 'testing-response' [1] here.
        So that some of the django testing assertions [2] can be used
        with selenium tests, too ;)

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

        [1] https://docs.djangoproject.com/en/1.11/topics/testing/tools/#testing-responses
        [2] https://docs.djangoproject.com/en/1.11/topics/testing/tools/#assertions
        """
        return selenium2fakes_response(self.driver, self.client, self.client_class)

    def _verbose_assertion_error(self, err):
        sys.stderr.write("\n\n")
        sys.stderr.flush()
        sys.stderr.write("*" * 79)
        sys.stderr.write("\n")

        traceback.print_exc()

        sys.stderr.write(" -" * 40)
        sys.stderr.write("\n")
        try:
            page_source = self.driver.page_source
        except Exception as e:
            print("Can't get 'driver.page_source': %s" % e)
        else:
            page_source = "\n".join([line for line in page_source.splitlines() if line.rstrip()])
            print(page_source, file=sys.stderr)

        sys.stderr.write("*" * 79)
        sys.stderr.write("\n")
        sys.stderr.write("\n\n")
        sys.stderr.flush()

        raise AssertionError(err)

    def assert_no_javascript_alert(self):
        alert = expected_conditions.alert_is_present()(self.driver)
        if alert != False:
            alert_text = alert.text
            alert.accept()  # Confirm a alert dialog, otherwise access to driver.page_source will failed!
            try:
                raise self.failureException("Alert is preset: %s" % alert_text)
            except AssertionError as err:
                self._verbose_assertion_error(err)

    def assert_equal_page_title(self, should):
        try:
            self.assertEqual(self.driver.title, should)
        except AssertionError as err:
            self._verbose_assertion_error(err)

    def assert_in_page_source(self, member):
        try:
            self.assertIn(member, self.driver.page_source)
        except AssertionError as err:
            self._verbose_assertion_error(err)

    def assert_not_in_page_source(self, member):
        try:
            self.assertNotIn(member, self.driver.page_source)
        except AssertionError as err:
            self._verbose_assertion_error(err)

    def assert_visible_by_id(self, id, timeout=10):
        """
        Test that an element by ID is present on the DOM of a page and visible.
        """
        locator = (By.ID, id)
        self._wait(
            conditions=expected_conditions.visibility_of_element_located(locator),
            timeout=timeout,
            msg="Wait for '#%s' to be visible. (timeout: %i)" % (id, timeout)
        )

    def assert_clickable_by_id(self, id, timeout=10):
        """
        Test that an element by ID is visible and enabled such that you can click it
        """
        locator = (By.ID, id)
        self._wait(
            conditions=expected_conditions.element_to_be_clickable(locator),
            timeout=timeout,
            msg="Wait for '#%s' to be clickable. (timeout: %i)" % (id, timeout)
        )

    def assert_clickable_by_xpath(self, xpath, timeout=10):
        """
        Test that an element by ID is visible and enabled such that you can click it
        """
        locator = (By.XPATH, xpath)
        self._wait(
            conditions=expected_conditions.element_to_be_clickable(locator),
            timeout=timeout,
            msg="Wait for '%s' to be clickable. (timeout: %i)" % (xpath, timeout)
        )


def find_executable(filename, extra_search_paths=None):
    """
    >>> find_executable("not existsing file", ["/foo", "/bar"])
    Traceback (most recent call last):
        ...
    FileNotFoundError: Can't find 'not existsing file' in PATH or ['/foo', '/bar']!

    >>> path = find_executable("python")
    >>> path.is_file()
    True
    """
    path = os.environ['PATH']
    paths = path.split(os.pathsep)

    if extra_search_paths:
        paths += list(extra_search_paths)

    for path in paths:
        path = Path(path, filename)
        if path.is_file():
            if not os.access(str(path), os.X_OK):
                raise FileNotFoundError("%s exists, but it's not executable!" % path)
            return path

    raise FileNotFoundError("Can't find %r in PATH or %s!" % (filename, extra_search_paths))


class SeleniumChromiumTestCase(SeleniumBaseTestCase):
    """
    TestCase with Selenium and the Chromium WebDriver
    Note:
        Needs 'chromium-chromedriver' executable!
        See README.creole for more info

    usage e.g.:

        from django_tools.unittest_utils.selenium_utils import SeleniumChromiumTestCase, chromium_available

        @unittest.skipUnless(chromium_available(), "Skip because Chromium is not available!")
        class ChromiumTests(SeleniumChromiumTestCase):

            def test_admin_login_page(self):
                self.driver.get(self.live_server_url + "/admin/login/")
                self.assert_equal_page_title("Log in | Django site admin")
                self.assert_in_page_source('<form action="/admin/login/" method="post" id="login-form">')
                self.assert_no_javascript_alert()

    see also: django_tools_tests/test_unittest_selenium.py
    """

    filename = "chromedriver"

    # Overwrite this in sub class, if needed:
    extra_search_paths = ('/usr/lib/chromium-browser',)

    options = (
        '--no-sandbox',
        '--headless',
        '--disable-gpu',
    )
    desired_capabilities = {
        'loggingPrefs': {
            'browser': 'ALL',
            'client': 'ALL',
            'driver': 'ALL',
            'performance': 'ALL',
            'server': 'ALL'
        },
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        chrome_options = webdriver.ChromeOptions()
        for argument in cls.options:
            chrome_options.add_argument(argument)

        try:
            executable = find_executable(cls.filename, cls.extra_search_paths)
        except FileNotFoundError:
            cls.driver = None
        else:
            desired = DesiredCapabilities.CHROME
            for key, value in cls.desired_capabilities.items():
                desired[key] = value

            cls.driver = webdriver.Chrome(
                chrome_options=chrome_options,
                executable_path=str(executable),  # Path() instance -> str()
                desired_capabilities=desired,
            )
            cls.driver.implicitly_wait(10)

    def get_browser_log(self):
        assert "browser" in self.driver.log_types
        browser_log = self.driver.get_log("browser")
        lines = []
        for entry in browser_log:
            lines.append(("{timestamp} {level} {source} {message}").format(**entry))
        return "\n".join(lines)

    def assert_in_browser_log(self, text):
        log = self.get_browser_log()
        print(log)
        self.assertIn(text, log)


def chromium_available(filename=None):
    """
    :return: True/False if 'chromium-chromedriver' executable can be found

    >>> chromium_available("doesn't exists")
    False
    """
    if filename is None:
        filename = SeleniumChromiumTestCase.filename

    try:
        executable = find_executable(filename, SeleniumChromiumTestCase.extra_search_paths)
    except FileNotFoundError as err:
        log.error("Chromium is no available: %s")
        return False

    log.debug("Chromium found here: %s" % executable)
    return True


class SeleniumFirefoxTestCase(SeleniumBaseTestCase):
    """
    TestCase with Selenium and the Firefox WebDriver
    Note:
        Needs 'geckodriver' executable!
        See README.creole for more info

    usage e.g.:

        from django_tools.unittest_utils.selenium_utils import SeleniumFirefoxTestCase, firefox_available

        @unittest.skipUnless(firefox_available(), "Skip because Firefox is not available!")
        class FirefoxTests(SeleniumFirefoxTestCase):

            def test_admin_login_page(self):
                self.driver.get(self.live_server_url + "/admin/login/")
                self.assert_equal_page_title("Log in | Django site admin")
                self.assert_in_page_source('<form action="/admin/login/" method="post" id="login-form">')
                self.assert_no_javascript_alert()

    see also: django_tools_tests/test_unittest_selenium.py
    """
    filename = "geckodriver"

    # Overwrite this in sub class, if needed:
    extra_search_paths = ()

    options = ('-headless',)
    desired_capabilities = {
        'loggingPrefs': {
            'browser': 'ALL',
            'client': 'ALL',
            'driver': 'ALL',
            'performance': 'ALL',
            'server': 'ALL'
        },
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        options = webdriver.FirefoxOptions()
        for argument in cls.options:
            options.add_argument(argument)

        try:
            executable = find_executable(cls.filename, cls.extra_search_paths)
        except FileNotFoundError:
            cls.driver = None
        else:
            desired = DesiredCapabilities.FIREFOX
            for key, value in cls.desired_capabilities.items():
                desired[key] = value

            cls.driver = webdriver.Firefox(
                firefox_options=options,
                executable_path=str(executable),  # Path() instance -> str()
                desired_capabilities=desired,
            )
            cls.driver.implicitly_wait(10)


def firefox_available(filename=None):
    """
    :return: True/False if 'firefox-chromedriver' executable can be found

    >>> firefox_available("doesn't exists")
    False
    """
    if filename is None:
        filename = SeleniumFirefoxTestCase.filename

    try:
        executable = find_executable(filename, SeleniumFirefoxTestCase.extra_search_paths)
    except FileNotFoundError as err:
        log.error("Firefox is no available: %s")
        return False

    log.debug("Firefox found here: %s" % executable)
    return True
