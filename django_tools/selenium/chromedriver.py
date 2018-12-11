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
                self.assert_in_page_source('<form action="/admin/login/" method="post" id="login-form">')
                self.assert_no_javascript_alert()

    see also: django_tools_tests/test_unittest_selenium.py
    """

    filename = "chromedriver"

    # Overwrite this in sub class, if needed:
    extra_search_paths = ("/usr/lib/chromium-browser",)

    options = ("--no-sandbox", "--headless", "--disable-gpu")
    desired_capabilities = {
        "loggingPrefs": {"browser": "ALL", "client": "ALL", "driver": "ALL", "performance": "ALL", "server": "ALL"}
    }

    @classmethod
    def setUpClass(cls):

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

        super().setUpClass()

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
