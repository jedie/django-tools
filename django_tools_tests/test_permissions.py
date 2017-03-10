# coding: utf-8


from __future__ import unicode_literals, print_function

import logging
import pprint

import pytest
from django.contrib import auth

from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from django_tools.permissions import check_permission, create_permission, \
    add_permissions, log_group_permissions, log_user_permissions, \
    get_admin_permissions, permissions2list, add_app_permissions, has_perm
from django_tools.unittest_utils.logging_utils import LoggingBuffer
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import create_user

from django_tools_test_project.django_tools_test_app.models import \
    LimitToUsergroupsTestModel

log = logging.getLogger(__name__)


PERMISSION_NAME="limittousergroupstestmodel.publish"


class TestCreatePermissions(TestCase):
    def test_create(self):
        permission = create_permission(
            permission=PERMISSION_NAME,
            name="Can Publish",
            model=LimitToUsergroupsTestModel
        )
        self.assertIsInstance(permission, Permission)
        self.assertEqual(permission.codename, "publish")


@pytest.fixture(scope="module")
def user_fixtures():
    create_user(username="normal_user", password="foobar")
    create_user(username="super_user", password="foobar", is_superuser=True)


@pytest.fixture(scope="module")
def permission_fixtures():
    create_permission(
        permission=PERMISSION_NAME,
        name="Can Publish",
        model=LimitToUsergroupsTestModel
    )


@pytest.mark.usefixtures(
    user_fixtures.__name__,
    permission_fixtures.__name__
)
class TestPermissions(BaseTestCase):
    def setUp(self):
        super(TestPermissions, self).setUp()
        self.create_testusers()
        self.normal_user = self._get_user(usertype="normal")
        self.superuser = self._get_user(usertype="superuser")
        self.permission = Permission.objects.get(codename="publish")
        self.group = Group.objects.create(name="Test User Group")
        self.normal_user.groups.add(self.group)
        self.normal_user.save()

    def test_setup(self):
        self.assertEqual(self.normal_user.get_all_permissions(), set())

    def test_add_permissions(self):
        self.assertEqual(
            check_permission(self.normal_user, PERMISSION_NAME, raise_exception=False),
            False
        )
        # permissions = self.get_all_permissions(self.normal_user)
        # self.assertEqual(permissions, "X")

        permissions=(
            (LimitToUsergroupsTestModel, "publish"),
        )
        add_permissions(permission_obj=self.group, permissions=permissions)

        # log_group_permissions(self.group)
        # log_user_permissions(self.normal_user)

        user = self.refresh_user(self.normal_user)
        # log_user_permissions(user)

        self.assertEqual(
            check_permission(user, "django_tools_test_app.publish", raise_exception=False),
            True
        )

        self.assertEqual(user.get_all_permissions(), {'django_tools_test_app.publish'})

    def test_superuser_check(self):
        self.assertEqual(
            check_permission(self.normal_user, "foo.bar", raise_exception=False),
            False
        )
        self.assertEqual(has_perm(self.normal_user, "foo.bar"), False)
        self.assertEqual(
            check_permission(self.superuser, "foo.bar", raise_exception=False),
            True
        )
        self.assertEqual(has_perm(self.superuser, "foo.bar"), True)

    def test_add_app_permissions(self):
        add_app_permissions(permission_obj=self.group, app_label="dynamic_site")
        permissions = self.group.permissions.all()
        permissions = permissions2list(permissions)
        pprint.pprint(permissions)
        self.assertEqual(permissions, [
            'dynamic_site.sitealias.add_sitealias',
            'dynamic_site.sitealias.change_sitealias',
            'dynamic_site.sitealias.delete_sitealias'
        ])

    def test_get_admin_permissions(self):
        permissions = get_admin_permissions()
        permissions = permissions2list(permissions)
        pprint.pprint(permissions)
        self.assertEqual(permissions, [
            'auth.group.add_group',
            'auth.group.change_group',
            'auth.group.delete_group',
            'auth.user.add_user',
            'auth.user.change_user',
            'auth.user.delete_user',
            'dynamic_site.sitealias.add_sitealias',
            'dynamic_site.sitealias.change_sitealias',
            'dynamic_site.sitealias.delete_sitealias',
            'filer.clipboard.add_clipboard',
            'filer.clipboard.change_clipboard',
            'filer.clipboard.delete_clipboard',
            'filer.file.add_file',
            'filer.file.change_file',
            'filer.file.delete_file',
            'filer.folder.add_folder',
            'filer.folder.can_use_directory_listing',
            'filer.folder.change_folder',
            'filer.folder.delete_folder',
            'filer.folderpermission.add_folderpermission',
            'filer.folderpermission.change_folderpermission',
            'filer.folderpermission.delete_folderpermission',
            'filer.image.add_image',
            'filer.image.change_image',
            'filer.image.delete_image',
            'filer.thumbnailoption.add_thumbnailoption',
            'filer.thumbnailoption.change_thumbnailoption',
            'filer.thumbnailoption.delete_thumbnailoption',
            'sites.site.add_site',
            'sites.site.change_site',
            'sites.site.delete_site'
        ])

    def test_has_perm_log(self):
        with LoggingBuffer(name=None, level=logging.ERROR) as log:
            self.assertEqual(has_perm(self.normal_user, "foo.bar1"), False)

        self.assertEqual(
            log.get_messages(),
            "DEBUG:django_tools.permissions:"
            "User normal test user has not foo.bar1"
        )

    def test_check_permission(self):
        with LoggingBuffer(name=None, level=logging.ERROR) as log:
            with self.assertRaises(PermissionDenied):
                check_permission(self.normal_user, "foo.bar2", raise_exception=True)

        log_messages = log.get_messages()
        print(log_messages)
        self.assertEqual(
            log_messages,
            'ERROR:django_tools.permissions:User "normal test user"'
            ' has not permission "foo.bar2" -> raise PermissionDenied!'
        )
