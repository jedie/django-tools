"""
    :created: 2015 by Jens Diemer
    :copyleft: 2015-2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import atexit
import logging
import pprint
import sys
import traceback
import unittest

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.manager import DriverManager

from django_tools.selenium.response import selenium2fakes_response


log = logging.getLogger(__name__)

WEB_DRIVER_INSTANCES = {}


@atexit.register
def quit_web_driver():
    for driver_name, driver in WEB_DRIVER_INSTANCES.items():
        if driver is not None:
            print(f'Quit {driver_name} web driver: {driver}')
            driver.quit()


class LocalStorage:
    """
    https://developer.mozilla.org/de/docs/Web/API/Window/localStorage

    Note:
        * Access "window.localStorage" works only *after* a request.
        * There's no type conversion!

    Otherwise, it ends in:

    selenium.common.exceptions.WebDriverException:
        Message: move target out of bounds:
            Failed to read the 'localStorage' property from 'Window':
            Storage is disabled inside 'data:' URLs.
    """

    def __init__(self, driver):
        self.driver = driver

    def items(self):
        return self.driver.execute_script(
            "var ls = window.localStorage, items = {}; "
            "for (var i = 0, k; i < ls.length; ++i) "
            "  items[k = ls.key(i)] = ls.getItem(k); "
            "return items; "
        )

    def keys(self):
        return self.driver.execute_script(
            "var ls = window.localStorage, keys = []; "
            "for (var i = 0; i < ls.length; ++i) "
            "  keys[i] = ls.key(i); "
            "return keys; "
        )

    def clear(self):
        self.driver.execute_script("window.localStorage.clear();")

    def __len__(self):
        return self.driver.execute_script("return window.localStorage.length;")

    def __getitem__(self, key):
        value = self.driver.execute_script("return window.localStorage.getItem(arguments[0]);", key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        self.driver.execute_script(
            "window.localStorage.setItem(arguments[0], arguments[1]);", key, value
        )

    def __contains__(self, key):
        return key in self.keys()

    def __repr__(self):
        return self.items().__str__()


def assert_browser_language(driver: RemoteWebDriver, languages: list):
    browser_languages = driver.execute_script('return window.navigator.languages')
    assert browser_languages == languages, (
        f'Browser language {browser_languages!r} is not in {languages!r}'
    )


class SeleniumBaseTestCase(unittest.TestCase):
    verbose_browser_name = None
    browser_binary_names = []
    web_driver_test_url = 'about:config'

    @classmethod
    def get_log_path(cls):
        return f'{cls.verbose_browser_name} {cls.__name__}.log'

    @classmethod
    def _get_service(cls, executable_path, ServiceClass):
        service = ServiceClass(
            executable_path=executable_path,
            log_path=cls.get_log_path(),
            # accept_languages doesn't work in headless mode
            # Set browser language via environment:
            env={
                'LANG': 'en_US.UTF-8',
                'LANGUAGE': 'en_US.UTF-8',
            },
        )
        return service

    @classmethod
    def get_executable_path(cls, manager: DriverManager):
        executable_path = manager.install()
        log.debug('Executable path from %s: %r', manager, executable_path)
        return executable_path

    @classmethod
    def check_web_driver(cls, driver):
        # Test if everything works:
        log.debug('Test %s requesting %r', driver, cls.web_driver_test_url)
        driver.get(cls.web_driver_test_url)
        current_url = driver.current_url
        if current_url == cls.web_driver_test_url:
            log.debug('Web driver %s works.', driver)
            return driver
        else:
            log.error('Error test request %r (got %r back)', cls.web_driver_test_url, current_url)
            driver.quit()

    @classmethod
    def _get_webdriver(cls):
        raise NotImplementedError

    @classmethod
    def get_webdriver(cls):
        """
        There are some problems if web drivers instance will be recreated.
        So use a "cache" for the instance and reuse existing instances.
        """
        if cls.verbose_browser_name in WEB_DRIVER_INSTANCES:
            driver = WEB_DRIVER_INSTANCES[cls.verbose_browser_name]
            log.info('resuse web driver %s for %s', driver, cls.verbose_browser_name)
        else:
            log.debug('Setup %s web driver', cls.verbose_browser_name)
            try:
                driver = cls._get_webdriver()
            except Exception as err:
                log.exception('Error init %s web driver: %s', cls.verbose_browser_name, err)
                driver = None
            WEB_DRIVER_INSTANCES[cls.verbose_browser_name] = driver

        return driver

    @classmethod
    def avaiable(cls):
        """
        Can be used in @unittest.skipUnless() decorator to skip tests
        if browser or webdriver is not available
        """
        driver = cls.get_webdriver()
        return driver is not None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = cls.get_webdriver()
        if cls.driver is not None:
            cls.local_storage = LocalStorage(cls.driver)

    def setUp(self):
        super().setUp()
        if self.driver is not None:
            self.driver.get(self.web_driver_test_url)
            self.driver.delete_all_cookies()

    def tearDown(self):
        super().tearDown()
        if self.driver is not None:
            # we clear window.localStorage here and not in setUp(), because
            # access "window.localStorage" works only *after* a request
            try:
                url = self.driver.current_url
            except Exception as err:
                log.exception('Error get current url: %s', err)
                return

            if url.startswith('http') and '://' in url:
                # We can't execute 'window.localStorage.clear();'
                # because Storage is disabled inside urls like: 'data:', 'about:...'
                self.local_storage.clear()

    def _wait(self, conditions, timeout=5, msg="wait timeout"):
        """
        Wait for the given condition.
        Display page_source on error.
        """
        try:
            check = WebDriverWait(self.driver, timeout).until(conditions)
        except TimeoutException as err:
            print(f"\nError: {msg}\n{err}\npage source:\n{self.driver.page_source}\n")
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
            print(f"Can't get 'driver.page_source': {e}")
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
        if alert:
            alert_text = alert.text

            # Confirm a alert dialog, otherwise access to driver.page_source will failed:
            alert.accept()
            try:
                raise self.failureException(f"Alert is preset: {alert_text}")
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
            msg=f"Wait for '#{id}' to be visible. (timeout: {timeout:d})",
        )

    def assert_clickable_by_id(self, id, timeout=10):
        """
        Test that an element by ID is visible and enabled such that you can click it
        """
        locator = (By.ID, id)
        self._wait(
            conditions=expected_conditions.element_to_be_clickable(locator),
            timeout=timeout,
            msg=f"Wait for '#{id}' to be clickable. (timeout: {timeout:d})",
        )

    def assert_clickable_by_xpath(self, xpath, timeout=10):
        """
        Test that an element by ID is visible and enabled such that you can click it
        """
        locator = (By.XPATH, xpath)
        self._wait(
            conditions=expected_conditions.element_to_be_clickable(locator),
            timeout=timeout,
            msg=f"Wait for '{xpath}' to be clickable. (timeout: {timeout:d})",
        )

    def assert_local_storage_key_value(self, *, key, value):
        print("local_storage:", pprint.pformat(self.local_storage))
        is_value = self.local_storage[key]
        self.assertEqual(value, is_value)

    def assert_browser_language(self, language: str):
        assert_browser_language(driver=self.driver, language=language)
