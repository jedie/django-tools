from bx_django_utils.test_utils.html_assertion import HtmlAssertionMixin
from django.contrib.auth.models import User
from django.test import TestCase
from model_bakery import baker

from django_tools import __version__


class AdminAnonymousTests(HtmlAssertionMixin, TestCase):
    """
    Anonymous will be redirected to the login page.
    """

    def test_login(self):
        response = self.client.get("/admin/")
        self.assertRedirects(response, expected_url="/admin/login/?next=/admin/")


class AdminLoggedinTests(HtmlAssertionMixin, TestCase):
    """
    Some basics test with the django admin
    """

    @classmethod
    def setUpTestData(cls):
        cls.superuser = baker.make(User, username='superuser', is_staff=True, is_active=True, is_superuser=True)
        cls.staffuser = baker.make(User, username='staff_test_user', is_staff=True, is_active=True, is_superuser=False)

    def test_staff_admin_index(self):
        self.client.force_login(self.staffuser)

        response = self.client.get("/admin/", HTTP_ACCEPT_LANGUAGE="en")
        self.assert_html_parts(
            response,
            parts=(
                f"<title>Site administration | django-tools v{__version__}</title>",
                "<h1>Site administration</h1>",
                "<strong>staff_test_user</strong>",
                "<p>You don’t have permission to view or edit anything.</p>",
            ),
        )
        self.assertTemplateUsed(response, template_name="admin/index.html")

    def test_superuser_admin_index(self):
        self.client.force_login(self.superuser)
        response = self.client.get("/admin/", HTTP_ACCEPT_LANGUAGE="en")
        self.assert_html_parts(
            response,
            parts=(
                "django_tools",
                "<strong>superuser</strong>",
                "Site administration",
                "/admin/auth/group/add/",
                "/admin/auth/user/add/",
            ),
        )
        self.assertTemplateUsed(response, template_name="admin/index.html")
