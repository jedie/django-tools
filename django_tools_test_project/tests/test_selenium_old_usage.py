"""
    :created: 11.12.2018 by Jens Diemer
    :copyleft: 2018-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import unittest

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.unittest_utils.selenium_utils import (
    SeleniumChromiumTestCase,
    SeleniumFirefoxTestCase,
    chromium_available,
    find_executable,
    firefox_available,
)


class TestWarnDecorators(unittest.TestCase):
    def test_SeleniumChromiumTestCase(self):

        with self.assertWarns(DeprecationWarning) as cm:
            SeleniumChromiumTestCase()

        assert_pformat_equal(
            str(cm.warning),
            "Use 'from django_tools.selenium.django import SeleniumChromiumStaticLiveServerTestCase' !",
        )

    def test_SeleniumFirefoxTestCase(self):

        with self.assertWarns(DeprecationWarning) as cm:
            SeleniumFirefoxTestCase()

        assert_pformat_equal(
            str(cm.warning), "Use 'from django_tools.selenium.django import SeleniumFirefoxStaticLiveServerTestCase' !"
        )

    def test_find_executable(self):

        with self.assertWarns(DeprecationWarning) as cm:
            find_executable("foobar")

        assert_pformat_equal(str(cm.warning), "Use 'from django_tools.selenium.utils import find_executable' !")

    def test_chromium_available(self):

        with self.assertWarns(DeprecationWarning) as cm:
            chromium_available()

        assert_pformat_equal(
            str(cm.warning), "Use 'from django_tools.selenium.chromedriver import chromium_available' !"
        )

    def test_firefox_available(self):

        with self.assertWarns(DeprecationWarning) as cm:
            firefox_available()

        assert_pformat_equal(
            str(cm.warning), "Use 'from django_tools.selenium.geckodriver import firefox_available' !"
        )
