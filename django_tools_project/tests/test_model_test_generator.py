"""
    :created: 24.04.2018 by Jens Diemer
    :copyleft: 2018-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from bx_django_utils.test_utils.html_assertion import HtmlAssertionMixin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth.models import User
from django.test import TestCase

from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.unittest_utils.user import TestUserMixin


class ModelTestGeneratorAdminTestCase(TestUserMixin, HtmlAssertionMixin, TestCase):

    def test_generate_code_action_exists(self):
        self.login(usertype="superuser")

        response = self.client.get("/admin/auth/user/")
        self.assert_html_parts(
            response,
            parts=(
                '<strong>superuser</strong>',
                '<option value="generate_test_code">Generate unittest code</option>',
            ),
        )
        self.assertTemplateUsed(response, "admin/change_list.html")

    def test_generate_code(self):
        self.login(usertype="superuser")

        user_pks = User.objects.all().values_list("pk", flat=True)

        response = self.client.post(
            path="/admin/auth/user/",
            data={"action": "generate_test_code", ACTION_CHECKBOX_NAME: user_pks, "index": 0},
            HTTP_ACCEPT_LANGUAGE="en",
        )
        # TODO: check content-type and filename!

        content = response.content.decode()
        must_contain = (
            'from auth.User',
            'django.contrib.auth.models.User',
            "user = User.objects.create(",
            "username='normal_test_user', # CharField, String (up to 150)",
            "username='staff_test_user', # CharField, String (up to 150)",
            "username='superuser', # CharField, String (up to 150)",
        )
        for part in must_contain:
            self.assertIn(part, content)

        headers = response.headers
        assert_pformat_equal(headers['content-disposition'], 'attachment; filename=auth.User.py')
        assert_pformat_equal(headers['content-type'], 'text/python')
