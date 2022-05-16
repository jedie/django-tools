from unittest import mock

from bx_django_utils.test_utils.html_assertion import (
    HtmlAssertionMixin,
    assert_html_response_snapshot,
)
from django.contrib.auth import get_user_model
from django.template.defaulttags import CsrfTokenNode
from django.test import TestCase
from model_bakery import baker

from django_tools_test_project.django_tools_test_app.models import VersioningTestModel


class ModelVersionProtectAdminTestCase(HtmlAssertionMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.super_user = baker.make(
            get_user_model(),
            id=1,
            username='TestUser',
            is_staff=True,
            is_superuser=True
        )

    def reset_client(self):
        self.client = self.client_class()
        self.client.force_login(self.super_user)

    def test_basic(self):
        self.client.force_login(self.super_user)

        # Get the "add new instance" form:

        with mock.patch.object(CsrfTokenNode, 'render', return_value='MockedCsrfTokenNode'):
            response = self.client.get(
                path="/admin/django_tools_test_app/versioningtestmodel/add/"
            )
        self.assert_html_parts(response, parts=(
            '<title>Add versioning test model | Django site admin</title>',
            '<input type="hidden" name="version" value="0" required id="id_version">'
        ))
        assert_html_response_snapshot(response, validate=False)

        assert VersioningTestModel.objects.count() == 0

        # Create new entry via admin:

        response = self.client.post(
            path="/admin/django_tools_test_app/versioningtestmodel/add/",
            data={
                'version': 0,
                'user': self.super_user.pk,
                'name': 'Add first Version',
                '_save': 'Save',
            },
        )
        self.assert_messages(response, expected_messages=[
            "The versioning test model"
            " “<a href=\"/admin/django_tools_test_app/versioningtestmodel/1/change/\">"
            "Add first Version (pk:1)</a>” was added successfully."
        ])
        self.assertRedirects(
            response,
            expected_url='/admin/django_tools_test_app/versioningtestmodel/',
            fetch_redirect_response=False
        )
        assert VersioningTestModel.objects.count() == 1
        instance = VersioningTestModel.objects.first()
        assert instance.name == 'Add first Version'
        assert instance.version == 1

        # Reset client to remove existing messages:
        self.reset_client()

        # Update the current version:

        response = self.client.post(
            path="/admin/django_tools_test_app/versioningtestmodel/1/change/",
            data={
                'version': 1,
                'user': self.super_user.pk,
                'name': 'A New Name',
                '_save': 'Save',
            },
        )
        self.assert_messages(response, expected_messages=[
            'The versioning test model'
            ' “<a href="/admin/django_tools_test_app/versioningtestmodel/1/change/">'
            'A New Name (pk:1)</a>” was changed successfully.'
        ])
        self.assertRedirects(
            response,
            expected_url='/admin/django_tools_test_app/versioningtestmodel/',
            fetch_redirect_response=False
        )
        instance = VersioningTestModel.objects.first()
        assert instance.name == 'A New Name'
        assert instance.version == 2

        # Error case: Try to overwrite with a older Version:

        with mock.patch.object(CsrfTokenNode, 'render', return_value='MockedCsrfTokenNode'):
            response = self.client.post(
                path="/admin/django_tools_test_app/versioningtestmodel/1/change/",
                data={
                    'version': 1,
                    'user': self.super_user.pk,
                    'name': 'Overwrite this!',
                    '_save': 'Save',
                },
            )
        self.assert_html_parts(response, parts=(
            '<li>Version error: Overwrite version 2 with 1 is forbidden!</li>',

            '<pre>- 2\n   + 1</pre>',

            '<li>changes between version 2 and 1:'
            '<pre>- &quot;A New Name&quot;\n   + &quot;Overwrite this!&quot;</pre></li>'
        ))
        assert_html_response_snapshot(response, validate=False)

        # Check that it's still version 2:
        instance = VersioningTestModel.objects.first()
        assert instance.name == 'A New Name'
        assert instance.version == 2
