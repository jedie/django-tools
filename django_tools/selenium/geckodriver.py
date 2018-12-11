"""
    :created: 2015 by Jens Diemer
    :copyleft: 2015-2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

# https://github.com/jedie/django-tools
from django_tools.selenium.base import SeleniumBaseTestCase
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

    filename = "geckodriver"

    # Overwrite this in sub class, if needed:
    extra_search_paths = ()

    options = ("-headless",)
    desired_capabilities = {
        "loggingPrefs": {"browser": "ALL", "client": "ALL", "driver": "ALL", "performance": "ALL", "server": "ALL"}
    }

    @classmethod
    def setUpClass(cls):
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

        super().setUpClass()


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
