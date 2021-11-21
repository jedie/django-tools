"""
    :created: 2015 by Jens Diemer
    :copyleft: 2015-2020 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import pprint
import shutil

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from django_tools.selenium.base import LocalStorage, SeleniumBaseTestCase, assert_browser_language


log = logging.getLogger(__name__)


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
    filename = 'chromedriver'

    options = (
        '--no-sandbox',
        '--headless',
        '--incognito',
        '--disable-gpu',
        '--disable-dev-shm-usage',  # https://bugs.chromium.org/p/chromedriver/issues/detail?id=2473
        '--lang=en-US'
    )
    desired_capabilities = {
        'loggingPrefs': {
            'browser': 'ALL',
            'driver': 'ALL',
            'performance': 'ALL',
        }
    }
    accept_languages = 'en-US,en;q=0.8'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        try:
            executable = shutil.which(cls.filename)
        except FileNotFoundError as err:
            log.exception('"%r" not found: %s', cls.filename, err)
        else:
            options = webdriver.ChromeOptions()
            options.add_experimental_option('w3c', False)  # needed to get browser logs
            options.add_experimental_option('prefs', {'intl.accept_languages': cls.accept_languages})
            options.add_argument(f'--accept-language="{cls.accept_languages}"')

            for argument in cls.options:
                options.add_argument(argument)

            for key, value in cls.desired_capabilities.items():
                options.set_capability(key, value)

            log.debug('Browser options:\n%s', pprint.pformat(options.to_capabilities()))
            service = Service(
                executable_path=str(executable),
                log_path=f'{cls.filename}.log'
            )
            cls.driver = webdriver.Chrome(
                options=options,
                service=service,
            )

            # Test may fail, if a other language is activated.
            # So check this after startup:
            assert_browser_language(driver=cls.driver, languages=('en', 'en-US'))

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


def chromium_available(filename=None):
    """
    :return: True/False if 'chromium-chromedriver' executable can be found

    >>> chromium_available("doesn't exists")
    False
    """
    if filename is None:
        filename = SeleniumChromiumTestCase.filename

    executable = shutil.which(filename)
    if not executable:
        log.error("Chromium is not available!")
        return False

    log.debug(f"Chromium found here: {executable}")
    return True
