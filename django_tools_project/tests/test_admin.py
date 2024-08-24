from bx_django_utils.test_utils.html_assertion import (
    HtmlAssertionMixin,
    assert_html_response_snapshot,
    get_django_name_suffix,
)
from django.contrib.auth.models import User
from django.test import TestCase
from model_bakery import baker


class AdminAnonymousTests(HtmlAssertionMixin, TestCase):
    """
    Anonymous will be redirected to the login page.
    """

    def test_login(self):
        response = self.client.get('/admin/')
        self.assertRedirects(response, expected_url='/admin/login/?next=/admin/')


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

        response = self.client.get("/admin/")
        self.assert_html_parts(
            response,
            parts=(
                "<h1>Site administration</h1>",
                "<strong>staff_test_user</strong>",
                "<p>You don’t have permission to view or edit anything.</p>",
            ),
        )
        self.assertTemplateUsed(response, template_name="admin/index.html")
        assert_html_response_snapshot(response, validate=False, name_suffix=get_django_name_suffix())

    def test_superuser_admin_index(self):
        self.client.force_login(self.superuser)
        response = self.client.get("/admin/")
        self.assert_html_parts(
            response,
            parts=(
                "<h1>Site administration</h1>",
                "django_tools",
                "<strong>superuser</strong>",
                "/admin/auth/group/add/",
                "/admin/auth/user/add/",
            ),
        )
        self.assertTemplateUsed(response, template_name="admin/index.html")
        assert_html_response_snapshot(response, validate=False, name_suffix=get_django_name_suffix())
