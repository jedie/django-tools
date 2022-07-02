from django.conf import settings
from django.contrib.auth.models import User
from django.test.client import Client
from playwright.sync_api import Page


def fast_login(page: Page, client: Client, live_server_url: str, user: User) -> None:
    """
    Helper to fast login, by injecting the session cookie.
    Usage, e.g.:
        fast_login(
            page=self.page,
            client=self.client,
            user=User.objects.create_superuser(username='a-user', password='ThisIsNotAPassword!'),
            live_server_url=self.live_server_url,
        )
    """
    # Create a session by using Django's test login:
    client.force_login(user=user)
    session_cookie = client.cookies[settings.SESSION_COOKIE_NAME]
    assert session_cookie

    # Inject the session Cookie to playwright browser:
    cookie_object = {
        'name': session_cookie.key,
        'value': session_cookie.value,
        'url': live_server_url,
    }
    page.context.add_cookies([cookie_object])
