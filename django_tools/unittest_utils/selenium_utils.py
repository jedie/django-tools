"""
    TODO: remove this file in future!

    :created: 2015 by Jens Diemer
    :copyleft: 2015-2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging

# https://github.com/jedie/django-tools
from django_tools.decorators import warn_class_usage, warn_function_usage
from django_tools.selenium.chromedriver import chromium_available as new_chromium_available
from django_tools.selenium.django import (
    SeleniumChromiumStaticLiveServerTestCase, SeleniumFirefoxStaticLiveServerTestCase
)
from django_tools.selenium.geckodriver import firefox_available as new_firefox_available
from django_tools.selenium.utils import find_executable as new_find_executable

log = logging.getLogger(__name__)


@warn_class_usage("Use 'from django_tools.selenium.django import SeleniumChromiumStaticLiveServerTestCase' !")
class SeleniumChromiumTestCase(SeleniumChromiumStaticLiveServerTestCase):
    pass


@warn_class_usage("Use 'from django_tools.selenium.django import SeleniumFirefoxStaticLiveServerTestCase' !")
class SeleniumFirefoxTestCase(SeleniumFirefoxStaticLiveServerTestCase):
    pass


@warn_function_usage("Use 'from django_tools.selenium.utils import find_executable' !")
def find_executable(*args, **kwargs):
    return new_find_executable(*args, **kwargs)


@warn_function_usage("Use 'from django_tools.selenium.geckodriver import firefox_available' !")
def firefox_available(*args, **kwargs):
    return new_firefox_available(*args, **kwargs)


@warn_function_usage("Use 'from django_tools.selenium.chromedriver import chromium_available' !")
def chromium_available(*args, **kwargs):
    return new_chromium_available(*args, **kwargs)
