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
from selenium.webdriver.firefox.webdriver import DEFAULT_EXECUTABLE_PATH

from django_tools.selenium.base import LocalStorage, SeleniumBaseTestCase
from django_tools.selenium.utils import find_executable


WEBDRIVER_BINARY_NAME = DEFAULT_EXECUTABLE_PATH  # e.g.: geckodriver


log = logging.getLogger(__name__)


def get_firefox_webdriver_path():
    return find_executable(WEBDRIVER_BINARY_NAME)


def get_firefox_browser_path():
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


def firefox_available():
    """
    :return: True/False if Firefox WebDriver + Browser is available
    """
    if get_firefox_webdriver_path() and get_firefox_browser_path():
        return True
    else:
        return False


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
                self.assert_in_page_source('<form action="/admin/login/" method="post" id="login-form">')
                self.assert_no_javascript_alert()

    see also: django_tools_tests/test_unittest_selenium.py
    """
    # Overwrite this in sub class, if needed:
    extra_search_paths = ()

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
    def setUpClass(cls):
        super().setUpClass()

        firefox_webdriver_path = get_firefox_webdriver_path()
        if not firefox_webdriver_path:
            return

        firefox_browser_path = get_firefox_browser_path()
        if not firefox_browser_path:
            return

        options = FirefoxOptions()
        options.binary = firefox_browser_path
        log.debug('binary location: %r', options.binary_location)

        for argument in cls.options:
            options.add_argument(argument)

        for key, value in cls.desired_capabilities.items():
            options.set_capability(key, value)

        options.set_preference('intl.accept_languages', 'en-US, en')

        log.debug('Browser options:\n%s', pprint.pformat(options.to_capabilities()))
        service = Service(
            executable_path=firefox_webdriver_path,
            log_path=f'geckodriver {cls.__name__}.log',
            env={
                'LANG': 'en_US.UTF-8',
                'LANGUAGE': 'en_US.UTF-8',
            }
        )
        cls.driver = webdriver.Firefox(
            options=options,
            service=service,
        )

        cls.local_storage = LocalStorage(cls.driver)
