
"""
    :created: 24.04.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from pprint import pprint

from django.contrib.auth.models import User

from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

from django.test import TestCase
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import TestUserMixin


class ModelTestGeneratorAdminTestCase(TestUserMixin, BaseTestCase, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_testusers(cls)

    def test_generate_code_action_exists(self):
        self.login(usertype="superuser")

        response = self.client.get("/admin/auth/user/")

        self.assertResponse(response,
            must_contain=(
                '<strong>superuser</strong>',
                '<option value="generate_test_code">Generate unittest code</option>',
            ),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            template_name="admin/change_list.html",
            messages=[],
            html=False,
            browser_traceback=True
        )

    def test_generate_code(self):
        self.login(usertype="superuser")

        user_pks = User.objects.all().values_list("pk", flat=True)

        response = self.client.post(
            path="/admin/auth/user/",
            data={
                "action": "generate_test_code",
                ACTION_CHECKBOX_NAME: user_pks,
                "index":0,
            },
            HTTP_ACCEPT_LANGUAGE="en"
        )
        # TODO: check content-type and filename!
        self.assertResponse(response,
            must_contain=(
                "from auth.User <class 'django.contrib.auth.models.User'>",
                'user = User.objects.create(',

                "username='normal_test_user', # CharField, String (up to 150)",
                "username='staff_test_user', # CharField, String (up to 150)",
                "username='superuser', # CharField, String (up to 150)",
            ),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            template_name=None,
            messages=[],
            html=False,
            browser_traceback=True
        )
        headers = response._headers
        pprint(headers)
        self.assertEqual(headers["content-disposition"],
            ('Content-Disposition', 'attachment; filename=auth.User.py')
        )
        self.assertEqual(headers["content-type"], ('Content-Type', 'text/python'))
