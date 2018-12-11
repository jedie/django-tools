"""
    :created: 11.12.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase

# https://github.com/jedie/django-tools
from django_tools.selenium.chromedriver import SeleniumChromiumTestCase
from django_tools.selenium.geckodriver import SeleniumFirefoxTestCase


class SeleniumChromiumStaticLiveServerTestCase(TestCase, StaticLiveServerTestCase, SeleniumChromiumTestCase):
    """
    inherit only from 'LiveServerTestCase' will result in
    a empty database after test run.

    See:

    https://github.com/pytest-dev/pytest-django/issues/613
    https://code.djangoproject.com/ticket/25251
    https://github.com/django/django/pull/7528
    """

    pass


class SeleniumFirefoxStaticLiveServerTestCase(TestCase, StaticLiveServerTestCase, SeleniumFirefoxTestCase):
    """
    inherit only from 'LiveServerTestCase' will result in
    a empty database after test run.

    See:

    https://github.com/pytest-dev/pytest-django/issues/613
    https://code.djangoproject.com/ticket/25251
    https://github.com/django/django/pull/7528
    """

    pass
