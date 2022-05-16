"""
    :created: 2015 by Jens Diemer
    :copyleft: 2015-2021 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging
import pprint

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

from django_tools.selenium.base import SeleniumBaseTestCase


log = logging.getLogger(__name__)


def firefox_available():
    return SeleniumFirefoxTestCase.avaiable()


class SeleniumFirefoxTestCase(SeleniumBaseTestCase):
    """
    TestCase with Selenium and the Firefox WebDriver
    Note:
        * Needs 'geckodriver' executable! See README.creole for more info
        * It's without django StaticLiveServerTestCase

    usage e.g.:

        from django_tools.selenium.geckodriver import SeleniumFirefoxTestCase, firefox_available

        @unittest.skipUnless(firefox_available(), "Skip because Firefox is not available!")
        class FirefoxTests(SeleniumFirefoxTestCase):

            def test_admin_login_page(self):
                self.driver.get(self.live_server_url + "/admin/login/")
                self.assert_equal_page_title("Log in | Django site admin")
                self.assert_in_page_source(
                    '<form action="/admin/login/" method="post" id="login-form">'
                )
                self.assert_no_javascript_alert()

    see also: django_tools_tests/test_unittest_selenium.py
    """

    verbose_browser_name = 'Firefox'

    options = (
        "-headless",
    )
    desired_capabilities = {
        "loggingPrefs": {
            "browser": "ALL",
            "client": "ALL",
            "driver": "ALL",
            "performance": "ALL",
            "server": "ALL"
        }
    }

    @classmethod
    def get_browser_binary_path(cls):
        binary = FirefoxBinary()
        try:
            path = binary._get_firefox_start_cmd()
        except RuntimeError as err:
            log.exception('Error getting binary: %s', err)
            assert 'Could not find firefox' in str(err)
        else:
            if not path:
                log.info('Firefox browser binary not found!')
            else:
                log.debug('Firefox binary found: "%s"', path)
                return path

    @classmethod
    def _get_webdriver(cls):
        executable_path = cls.get_executable_path(manager=GeckoDriverManager())
        if executable_path is None:
            return

        browser_path = cls.get_browser_binary_path()
        if browser_path is None:
            log.debug('No browser path')
            return
        log.debug('Browser path: %r', browser_path)

        options = FirefoxOptions()
        options.binary = browser_path

        for argument in cls.options:
            options.add_argument(argument)

        for key, value in cls.desired_capabilities.items():
            options.set_capability(key, value)

        options.set_preference('intl.accept_languages', 'en-US, en')

        # https://github.com/mozilla/geckodriver/issues/284#issuecomment-458305621
        options.set_preference('devtools.console.stdout.content', True)

        log.debug('Browser options:\n%s', pprint.pformat(options.to_capabilities()))
        service = cls._get_service(executable_path, ServiceClass=Service)

        return cls.check_web_driver(
            webdriver.Firefox(
                options=options,
                service=service,
            )
        )
