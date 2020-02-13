"""
    :created: 11.12.2018 by Jens Diemer
    :copyleft: 2018-2020 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from django_tools.selenium.chromedriver import SeleniumChromiumTestCase
from django_tools.selenium.geckodriver import SeleniumFirefoxTestCase


class SeleniumChromiumStaticLiveServerTestCase(StaticLiveServerTestCase, SeleniumChromiumTestCase):
    pass


class SeleniumFirefoxStaticLiveServerTestCase(StaticLiveServerTestCase, SeleniumFirefoxTestCase):
    pass
