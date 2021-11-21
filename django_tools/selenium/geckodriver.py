"""
    :created: 2015 by Jens Diemer
    :copyleft: 2015-2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging
import pprint

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import DEFAULT_EXECUTABLE_PATH

from django_tools.selenium.base import LocalStorage, SeleniumBaseTestCase, assert_browser_language
from django_tools.selenium.utils import find_executable


log = logging.getLogger(__name__)


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

    filename = DEFAULT_EXECUTABLE_PATH

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

        try:
            executable = find_executable(cls.filename, cls.extra_search_paths)
        except FileNotFoundError as err:
            log.exception('"%r" not found: %s', cls.filename, err)
        else:
            options = FirefoxOptions()

            for argument in cls.options:
                options.add_argument(argument)

            for key, value in cls.desired_capabilities.items():
                options.set_capability(key, value)

            options.set_preference('intl.accept_languages', 'en-US, en')

            log.debug('Browser options:\n%s', pprint.pformat(options.to_capabilities()))
            service = Service(
                executable_path=str(executable),
                log_path=f'{cls.filename}.log'
            )
            cls.driver = webdriver.Firefox(
                options=options,
                service=service,
            )

            # Test may fail, if a other language is activated.
            # So check this after startup:
            assert_browser_language(driver=cls.driver, languages=('en', 'en-US'))

            cls.local_storage = LocalStorage(cls.driver)


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
        log.error("Firefox is not available: %s", err)
        return False

    log.debug(f"Firefox found here: {executable}")
    return True
