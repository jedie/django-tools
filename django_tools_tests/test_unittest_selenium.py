
"""
    :created: 13.06.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from django.conf import settings
from django.contrib import auth
from django.test import override_settings

from selenium.common.exceptions import NoSuchElementException

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.selenium_utils import SeleniumChromiumTestCase
from django_tools.unittest_utils.user import TestUserMixin


@override_settings(DEBUG=True)
class SeleniumChromiumAdminTests(TestUserMixin, SeleniumChromiumTestCase):
    def test_login(self):

        self.assertTrue(settings.DEBUG)

        staff_data = self.get_userdata("staff")

        login_button_xpath='//input[@value="Log in"]'

        url = self.live_server_url + "/admin/login/?next=/admin/"
        self.driver.get(url)
        # self._wait(
        #     conditions=expected_conditions.element_to_be_clickable(
        #          (By.XPATH, login_button_xpath)
        #     ),
        #     timeout=3,
        #     msg="Wait for 'login button' text",
        # )

        self.assert_in_page_source("Log in | Django site admin")
        self.assert_not_in_page_source("errornote")
        self.assert_not_in_page_source("Please enter the correct username and password")

        try:
            username_input = self.driver.find_element_by_name("username")
            username_input.send_keys(staff_data["username"])

            password_input = self.driver.find_element_by_name("password")
            password_input.send_keys(staff_data["password"])

            login_button = self.driver.find_element_by_xpath(login_button_xpath)
            login_button.click()
        except NoSuchElementException as ex:
            self.fail(ex.msg)

        # self._wait(
        #     conditions=expected_conditions.element_to_be_clickable(
        #          (By.ID, "foo bar...")
        #     ),
        #     timeout=10,
        #     msg="Wait for 'login button' text",
        # )

        self.assert_no_javascript_alert()
        self.assert_equal_page_title("Site administration | Django site admin")
        self.assert_in_page_source("<strong>staff_test_user</strong>")
        self.assert_not_in_page_source("errornote")
        self.assert_not_in_page_source("Please enter the correct username and password")

    def test_admin_static_files(self):
        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.assert_in_page_source('href="/static/admin/css/base.css"')

        self.driver.get(self.live_server_url + "/static/admin/css/base.css")
        self.assert_in_page_source('margin: 0;')
        self.assert_in_page_source('padding: 0;')
