"""
    :created: 2015 by Jens Diemer
    :copyleft: 2015-2021 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import pprint

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from django_tools.selenium.base import LocalStorage, SeleniumBaseTestCase
from django_tools.selenium.utils import find_executable


WEBDRIVER_BINARY_NAME = 'chromedriver'
BROWSER_BINARY_NAMES = ['chrome', 'chromium']


log = logging.getLogger(__name__)


def get_chromium_webdriver_path():
    return find_executable(WEBDRIVER_BINARY_NAME)


def get_chromium_browser_path():
    for name in BROWSER_BINARY_NAMES:
        path = find_executable(name)
        if path:
            return path


def chromium_available():
    """
    :return: True/False if Chromium WebDriver + Browser is available
    """
    if get_chromium_webdriver_path() and get_chromium_browser_path():
        return True
    else:
        return False


class SeleniumChromiumTestCase(SeleniumBaseTestCase):
    """
    TestCase with Selenium and the Chromium WebDriver
    Note:
        * Needs 'chromium-chromedriver' executable! See README.creole for more info
        * It's without django StaticLiveServerTestCase

    usage e.g.:

        from django_tools.selenium.chromedriver import SeleniumChromiumTestCase, chromium_available

        @unittest.skipUnless(chromium_available(), "Skip because Chromium is not available!")
        class ChromiumTests(SeleniumChromiumTestCase):

            def test_admin_login_page(self):
                self.driver.get(self.live_server_url + "/admin/login/")
                self.assert_equal_page_title("Log in | Django site admin")
                self.assert_in_page_source(
                    '<form action="/admin/login/" method="post" id="login-form">'
                )
                self.assert_no_javascript_alert()

    see also: django_tools_tests/test_unittest_selenium.py
    """
    options = (
        '--no-sandbox',
        '--headless',
        '--incognito',
        '--disable-gpu',
        '--disable-dev-shm-usage',  # https://bugs.chromium.org/p/chromedriver/issues/detail?id=2473
    )
    desired_capabilities = {
        'loggingPrefs': {
            'browser': 'ALL',
            'driver': 'ALL',
            'performance': 'ALL',
        }
    }
    accept_languages = 'en-US'

    # Start a W3C compliant browser?
    # Note: If you would like to access browser console log, then it must be: False!
    # But in False mode, some silenoum conditions will not work!
    # See: https://github.com/SeleniumHQ/selenium/issues/10071
    w3c = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        chromium_webdriver_path = get_chromium_webdriver_path()
        if not chromium_webdriver_path:
            return

        if not get_chromium_browser_path():
            return

        options = webdriver.ChromeOptions()

        options.add_experimental_option('w3c', cls.w3c)

        # Note: accept_languages will be ignored in headless mode!
        # See: https://github.com/jedie/django-tools/issues/21
        # Work-a-round: set via "env" in Service() below
        options.add_experimental_option('prefs', {'intl.accept_languages': cls.accept_languages})

        for argument in cls.options:
            options.add_argument(argument)

        for key, value in cls.desired_capabilities.items():
            options.set_capability(key, value)

        log.debug('Browser options:\n%s', pprint.pformat(options.to_capabilities()))
        service = Service(
            executable_path=chromium_webdriver_path,
            log_path=f'chromedriver {cls.__name__}.log',

            # accept_languages doesn't work in headless mode
            # Set browser language via environment:
            env={  # noqa -> https://github.com/SeleniumHQ/selenium/pull/10072
                'LANG': 'en_US.UTF-8',
                'LANGUAGE': 'en_US.UTF-8',
            }
        )
        cls.driver = webdriver.Chrome(
            options=options,
            service=service,
        )

        cls.local_storage = LocalStorage(cls.driver)

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
