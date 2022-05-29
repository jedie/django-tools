"""
    :created: 2015 by Jens Diemer
    :copyleft: 2015-2021 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import pprint

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

from django_tools.selenium.base import SeleniumBaseTestCase


log = logging.getLogger(__name__)


def chromium_available():
    return SeleniumChromiumTestCase.avaiable()


class SeleniumChromiumTestCase(SeleniumBaseTestCase):
    """
    TestCase with Selenium and the Chromium/Chrome WebDriver
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

    verbose_browser_name = 'Chromium'
    browser_binary_names = ['chromium', 'chrome']

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
    # But in False mode, some selenium conditions will not work!
    # See: https://github.com/SeleniumHQ/selenium/issues/10071
    w3c = True

    CHROME_TYPES = (ChromeType.CHROMIUM, ChromeType.GOOGLE, ChromeType.MSEDGE)

    @classmethod
    def _get_options(cls):
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
        return options

    @classmethod
    def _get_webdriver(cls):
        for chrome_type in cls.CHROME_TYPES:
            log.debug('Try %r', chrome_type)
            try:
                executable_path = cls.get_executable_path(
                    manager=ChromeDriverManager(chrome_type=chrome_type)
                )
                if not executable_path:
                    continue

                options = cls._get_options()
                service = cls._get_service(executable_path, ServiceClass=Service)

                driver = cls.check_web_driver(
                    webdriver.Chrome(
                        options=options,
                        service=service,
                    )
                )
                if driver is not None:
                    return driver
            except Exception as err:
                log.exception('Can not setup %r: %s', chrome_type, err)

    def get_browser_log(self):
        assert self.w3c is False, (
            'Accessing the logs is only available in non W3C mode!'
            ' See: https://github.com/SeleniumHQ/selenium/issues/10071'
        )
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
