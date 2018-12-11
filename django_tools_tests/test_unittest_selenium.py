"""
    :created: 13.06.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import os
import tempfile
import unittest
from pathlib import Path

from django.conf import settings
from django.contrib import auth
from django.test import override_settings

from selenium.common.exceptions import NoSuchElementException

# https://github.com/jedie/django-tools
from django_tools.selenium.base import SeleniumBaseTestCase
from django_tools.selenium.chromedriver import SeleniumChromiumTestCase, chromium_available
from django_tools.selenium.django import (
    SeleniumChromiumStaticLiveServerTestCase, SeleniumFirefoxStaticLiveServerTestCase
)
from django_tools.selenium.geckodriver import SeleniumFirefoxTestCase, firefox_available
from django_tools.selenium.utils import find_executable
from django_tools.unittest_utils.user import TestUserMixin


@unittest.skipUnless(chromium_available(), "Skip because Chromium is not available!")
class ExampleChromiumTests(SeleniumChromiumStaticLiveServerTestCase):
    def test_admin_login_page(self):
        self.driver.get(self.live_server_url + "/admin/login/")
        self.assert_equal_page_title("Log in | Django site admin")
        self.assert_in_page_source('<form action="/admin/login/" method="post" id="login-form">')
        self.assert_no_javascript_alert()


@unittest.skipUnless(firefox_available(), "Skip because Firefox is not available!")
class ExampleFirefoxTests(SeleniumFirefoxStaticLiveServerTestCase):
    def test_admin_login_page(self):
        self.driver.get(self.live_server_url + "/admin/login/")
        self.assert_equal_page_title("Log in | Django site admin")
        self.assert_in_page_source('<form action="/admin/login/" method="post" id="login-form">')
        self.assert_no_javascript_alert()


class SeleniumHelperTests(unittest.TestCase):
    def test_find_executable(self):
        with tempfile.NamedTemporaryFile(prefix="test_not_executable_", delete=False) as f:
            filepath = Path(f.name).resolve()
            self.assertTrue(filepath.is_file())
            name = filepath.name
            path = filepath.parent

            # File is not in PATH:
            with self.assertRaises(FileNotFoundError) as context_manager:
                find_executable(name)

            self.assertEqual(context_manager.exception.args, ("Can't find '%s' in PATH or None!" % name,))

            old_path = os.environ["PATH"]
            try:
                # File is in PATH, but not executable:
                os.environ["PATH"] += "%s%s" % (os.pathsep, path)
                with self.assertRaises(FileNotFoundError) as context_manager:
                    find_executable(name)

                self.assertEqual(context_manager.exception.args, ("%s exists, but it's not executable!" % filepath,))

                # File is in PATH and executable:
                filepath.chmod(0x777)
                result = find_executable(name)
                self.assertEqual(result, filepath)
            finally:
                os.environ["PATH"] = old_path

            # Executable file is not in PATH, but can be found via extra_search_paths:
            result = find_executable(name, extra_search_paths=(path,))
            self.assertEqual(result, filepath)


class SeleniumTestsMixin:
    def test_login(self):

        self.assertTrue(settings.DEBUG)

        staff_data = self.get_userdata("staff")

        login_button_xpath = '//input[@value="Log in"]'

        url = self.live_server_url + "/admin/login/?next=/admin/"
        self.driver.get(url)

        self.assert_in_page_source("Log in | Django site admin")
        self.assert_not_in_page_source("errornote")
        self.assert_not_in_page_source("Please enter the correct username and password")

        self.assert_visible_by_id("id_username", timeout=2)
        self.assert_clickable_by_id("id_password", timeout=2)
        self.assert_clickable_by_xpath(login_button_xpath, timeout=2)

        try:
            username_input = self.driver.find_element_by_name("username")
            username_input.send_keys(staff_data["username"])

            password_input = self.driver.find_element_by_name("password")
            password_input.send_keys(staff_data["password"])

            login_button = self.driver.find_element_by_xpath(login_button_xpath)
            login_button.click()
        except NoSuchElementException as ex:
            self.fail(ex.msg)

        self.assert_no_javascript_alert()
        self.assert_not_in_page_source("Please enter the correct username and password")
        self.assert_not_in_page_source("errornote")
        self.assert_equal_page_title("Site administration | Django site admin")
        self.assert_in_page_source("<strong>staff_test_user</strong>")

        self.assert_visible_by_id("user-tools", timeout=2)
        self.assert_clickable_by_id("site-name", timeout=2)

    def test_admin_static_files(self):
        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.assert_in_page_source('href="/static/admin/css/base.css"')

        self.driver.get(self.live_server_url + "/static/admin/css/base.css")
        self.assert_in_page_source("margin: 0;")
        self.assert_in_page_source("padding: 0;")

    def test_local_storage_access(self):
        self.driver.get(self.live_server_url + "/")

        self.assertEqual(len(self.local_storage), 0)

        with self.assertRaises(KeyError) as cm:
            self.assert_local_storage_key_value(key="foo", value="bar")
        self.assertEqual(cm.exception.args[0], "foo")

        self.local_storage["bar"] = "foo"
        self.assertEqual(len(self.local_storage), 1)
        self.assert_local_storage_key_value(key="bar", value="foo")

        self.assertIn("bar", self.local_storage)

        self.assertEqual(repr(self.local_storage), "{'bar': 'foo'}")

        # There's no type conversion!
        self.local_storage["one"] = 1
        self.local_storage["t"] = True
        self.local_storage["f"] = False

        self.assertEqual(self.local_storage.items(), {"bar": "foo", "f": "false", "t": "true", "one": "1"})
        self.local_storage.clear()

        self.assertEqual(self.local_storage.items(), {})

        self.local_storage["foo"] = "bar"
        self.assertEqual(self.local_storage.items(), {"foo": "bar"})

        self.tearDown() # tearDown should clear the local_storage
        self.assertEqual(self.local_storage.items(), {})


@override_settings(DEBUG=True)
@unittest.skipUnless(chromium_available(), "Skip because Chromium is not available!")
class SeleniumChromiumAdminTests(TestUserMixin, SeleniumChromiumStaticLiveServerTestCase, SeleniumTestsMixin):
    def test_console(self):
        self.driver.get(self.live_server_url + "/")

        self.driver.execute_script("console.log('test console output 1');")
        self.assert_in_browser_log("test console output 1")

        self.driver.execute_script("console.log('test console output 2');")
        self.assert_in_browser_log("test console output 2")


@override_settings(DEBUG=True)
@unittest.skipUnless(firefox_available(), "Skip because Firefox is not available!")
class SeleniumFirefoxAdminTests(TestUserMixin, SeleniumFirefoxStaticLiveServerTestCase, SeleniumTestsMixin):
    pass


class NonStaticLiveServerMixin:
    def test_google(self):
        self.driver.get("https://www.google.com/")
        self.assert_equal_page_title("Google")
        self.assert_in_page_source("Google Inc.")


@unittest.skipUnless(chromium_available(), "Skip because Chromium is not available!")
class TestSeleniumChromiumNonStaticLiveServer(SeleniumChromiumTestCase, NonStaticLiveServerMixin):
    pass


@unittest.skipUnless(firefox_available(), "Skip because Firefox is not available!")
class TestSeleniumFirefoxNonStaticLiveServer(SeleniumFirefoxTestCase, NonStaticLiveServerMixin):
    pass
