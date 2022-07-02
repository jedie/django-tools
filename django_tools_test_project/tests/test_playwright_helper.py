from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpRequest
from playwright.sync_api import Page, expect

from django_tools.playwright.base import PyTestPlaywrightBaseTestCase
from django_tools.playwright.utils import fast_login


class PyTestPlaywrightTestCase(PyTestPlaywrightBaseTestCase):
    def test_setup_pytest_fixture(self):
        assert hasattr(self, 'page')
        page = self.page
        assert isinstance(page, Page)

    def test_admin_login(self):
        # Create a User:
        username = 'a-user'
        password = 'ThisIsNotAPassword!'
        superuser = User.objects.create_superuser(username=username, password=password)
        superuser.full_clean()

        # Use can login?
        user = authenticate(request=HttpRequest(), username=username, password=password)
        assert isinstance(user, User)

        # Redirect to login?
        self.page.goto(f'{self.live_server_url}/admin/')
        expect(self.page).to_have_url(f'{self.live_server_url}/admin/login/?next=/admin/')
        expect(self.page).to_have_title('Log in | Django site admin')

        # Login:
        self.page.type('#id_username', username)
        self.page.type('#id_password', password)
        self.page.locator('text=Log in').click()

        # Are we logged in?
        expect(self.page).to_have_url(f'{self.live_server_url}/admin/')
        expect(self.page).to_have_title('Site administration | Django site admin')

    def test_fast_login(self):
        fast_login(
            page=self.page,
            client=self.client,
            user=User.objects.create_superuser(username='a-user', password='ThisIsNotAPassword!'),
            live_server_url=self.live_server_url,
        )

        # Are we logged in?
        self.page.goto(f'{self.live_server_url}/admin/')
        expect(self.page).to_have_url(f'{self.live_server_url}/admin/')
        expect(self.page).to_have_title('Site administration | Django site admin')
