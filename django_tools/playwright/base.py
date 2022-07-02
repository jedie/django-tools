import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.async_api import Page


@pytest.mark.playwright
class PyTestPlaywrightBaseTestCase(StaticLiveServerTestCase):
    """
    A base class for Unittest class based Playwright tests,
    using pytest-playwright fixtures:
      * Based on Django's StaticLiveServerTestCase.
      * Setup a Playwright Page instance.
      * Mark all tests with "playwright".
    """

    @pytest.fixture(autouse=True)
    def setup_pytest_fixture(self, page: Page):
        self.page = page
