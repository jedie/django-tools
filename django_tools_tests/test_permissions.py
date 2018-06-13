# coding: utf-8


from __future__ import print_function, unicode_literals

import logging
import pprint

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.test import override_settings

from django_tools_test_project.django_tools_test_app.models import LimitToUsergroupsTestModel, PermissionTestModel

# https://github.com/jedie/django-tools
from django_tools.permissions import (
    add_app_permissions, add_permissions, check_permission, get_admin_permissions, get_filtered_permissions,
    get_permission_by_string, has_perm, log_group_permissions, log_user_permissions, permissions2list,
    pprint_filtered_permissions
)
from django_tools.unittest_utils.logging_utils import LoggingBuffer
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import TestUserMixin

log = logging.getLogger(__name__)


@override_settings(DEBUG = True)
class TestPermissions(TestUserMixin, BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestPermissions, cls).setUpTestData()

        cls.extra_permission = get_permission_by_string(
            permission="django_tools_test_app.extra_permission"
        )

        cls.instance = PermissionTestModel.objects.create(foo="bar")

    def setUp(self):
        super(TestPermissions, self).setUp()

        users = User.objects.all()
        usernames = users.values_list("username", flat=True).order_by("username")
        assert tuple(usernames) == ('normal_test_user', 'staff_test_user', 'superuser')

        self.superuser = self._get_user(usertype="superuser")

        # The "staff user" has some permissions:
        self.staff_user = self._get_user(usertype="staff")
        self.staff_group = Group.objects.create(name="Staff User Group")
        self.staff_group.permissions.add(self.extra_permission)
        self.staff_group.permissions.add(get_permission_by_string("django_tools_test_app.add_permissiontestmodel"))
        self.staff_group.permissions.add(get_permission_by_string("django_tools_test_app.change_permissiontestmodel"))
        self.staff_group.permissions.add(get_permission_by_string("django_tools_test_app.delete_permissiontestmodel"))
        self.staff_user.groups.add(self.staff_group)
        self.staff_user.save()

        # The "normal user" has no permissions:
        self.normal_user = self._get_user(usertype="normal")
        self.normal_group = Group.objects.create(name="Normal User Group")
        self.normal_user.groups.add(self.normal_group)
        self.normal_user.save()

    #-------------------------------------------------------------------------

    def assert_permissiontestmodel(self, permission):
        self.assertIsInstance(permission, Permission)
        self.assertIsInstance(permission.content_type, ContentType)

        self.assertEqual(permission.content_type.app_label, "django_tools_test_app")
        self.assertEqual(permission.content_type.model, "permissiontestmodel")

    def assert_extra_permission(self, permission):
        self.assert_permissiontestmodel(permission)
        self.assertEqual(permission.codename, "extra_permission")

    #-------------------------------------------------------------------------

    def test_setup(self):
        self.assert_extra_permission(self.extra_permission)

        # The "normal user" has no permissions
        self.assertEqual(self.normal_user.get_all_permissions(), set())

        # The "staff user" has some permissions
        self.assertEqual(self.staff_user.get_all_permissions(),
            {
                "django_tools_test_app.extra_permission",
                "django_tools_test_app.add_permissiontestmodel",
                "django_tools_test_app.change_permissiontestmodel",
                "django_tools_test_app.delete_permissiontestmodel",
            }
        )

        all_permissions = [
            "%s.%s" % (entry.content_type, entry.codename)
            for entry in Permission.objects.all()
        ]
        pprint.pprint(all_permissions)

        # Default mode permissions:
        self.assertIn("permission test model.add_permissiontestmodel", all_permissions)
        self.assertIn("permission test model.change_permissiontestmodel", all_permissions)
        self.assertIn("permission test model.delete_permissiontestmodel", all_permissions)

        # Own permission defined via Meta.permissions:
        self.assertIn("permission test model.extra_permission", all_permissions)

    #-------------------------------------------------------------------------

    def test_get_default_permissions(self):
        # https://docs.djangoproject.com/en/1.8/ref/models/options/#default-permissions
        permission = get_permission_by_string("django_tools_test_app.add_permissiontestmodel")
        self.assert_permissiontestmodel(permission)
        self.assertEqual(permission.codename, "add_permissiontestmodel")

        permission = get_permission_by_string("django_tools_test_app.change_permissiontestmodel")
        self.assert_permissiontestmodel(permission)
        self.assertEqual(permission.codename, "change_permissiontestmodel")

        permission = get_permission_by_string("django_tools_test_app.delete_permissiontestmodel")
        self.assert_permissiontestmodel(permission)
        self.assertEqual(permission.codename, "delete_permissiontestmodel")

    def test_get_extra_permission(self):
        # https://docs.djangoproject.com/en/1.8/ref/models/options/#permissions
        permission = get_permission_by_string("django_tools_test_app.extra_permission")
        self.assert_extra_permission(permission)

    #-------------------------------------------------------------------------

    def test_get_permission_wrong_format(self):
        with self.assertRaises(PermissionDenied) as cm:
            get_permission_by_string("no_dot_in_string")

        self.assert_exception_startswith(cm, "Wrong permission string format")

    def test_get_permission_wrong_app_label(self):
        with self.assertRaises(PermissionDenied) as cm:
            get_permission_by_string("wrong.foobar")

        self.assert_exception_startswith(cm,
            "App label 'wrong' from permission 'wrong.foobar' doesn't exists!"
        )

    def test_get_permission_wrong_codename(self):
        with self.assertRaises(PermissionDenied) as cm:
            get_permission_by_string("auth.wrong")

        self.assert_exception_startswith(cm,
            "Codename 'wrong' from permission 'auth.wrong' doesn't exists!"
        )

    #-------------------------------------------------------------------------

    def test_add_permissions(self):
        permissions = (
            (LimitToUsergroupsTestModel, "extra_permission"),
        )
        add_permissions(permission_obj=self.normal_group, permissions=permissions)

        user = self.refresh_user(self.normal_user)
        self.assertEqual(user.get_all_permissions(), {'django_tools_test_app.extra_permission'})

    def test_check_permission_error_without_exception(self):
        self.assertFalse(
            check_permission(
                self.normal_user,
                "django_tools_test_app.extra_permission",
                raise_exception=False
            )
        )

    def test_check_permission_error_with_exception(self):
        with self.assertRaises(PermissionDenied) as cm:
            check_permission(self.normal_user, "django_tools_test_app.extra_permission")

        self.assertFalse(hasattr(cm, "args")) # No error message

    def test_check_permission_existing(self):
        self.assertTrue(
            check_permission(
                self.staff_user,
                "django_tools_test_app.extra_permission",
            )
        )

    #-------------------------------------------------------------------------

    def test_check_permission_wrong_format(self):
        check_permission(self.superuser, "no_dot_in_string") # superuser can do everything ;)

        with self.assertRaises(PermissionDenied) as cm:
            check_permission(self.staff_user, "no_dot_in_string")

        self.assert_exception_startswith(cm, "Wrong permission string format")

    def test_check_permission_wrong_app_label(self):
        check_permission(self.superuser, "wrong.foobar") # superuser can do everything ;)

        with self.assertRaises(PermissionDenied) as cm:
            check_permission(self.staff_user, "wrong.foobar")

        self.assert_exception_startswith(cm,
            "App label 'wrong' from permission 'wrong.foobar' doesn't exists!"
        )

    def test_check_permission_wrong_codename(self):
        check_permission(self.superuser, "auth.wrong") # superuser can do everything ;)

        with self.assertRaises(PermissionDenied) as cm:
            check_permission(self.staff_user, "auth.wrong")

        self.assert_exception_startswith(cm,
            "Codename 'wrong' from permission 'auth.wrong' doesn't exists!"
        )

    def test_get_admin_permissions(self):
        permissions = get_admin_permissions()
        permissions = permissions2list(permissions)
        pprint.pprint(permissions)
        self.assertEqual(permissions, [
            'auth.add_group',
            'auth.change_group',
            'auth.delete_group',
            'auth.add_user',
            'auth.change_user',
            'auth.delete_user',
            'django_tools_test_app.add_permissiontestmodel',
            'django_tools_test_app.change_permissiontestmodel',
            'django_tools_test_app.delete_permissiontestmodel',
            'django_tools_test_app.extra_permission',
            'filer.add_clipboard',
            'filer.change_clipboard',
            'filer.delete_clipboard',
            'filer.add_file',
            'filer.change_file',
            'filer.delete_file',
            'filer.add_folder',
            'filer.can_use_directory_listing',
            'filer.change_folder',
            'filer.delete_folder',
            'filer.add_folderpermission',
            'filer.change_folderpermission',
            'filer.delete_folderpermission',
            'filer.add_image',
            'filer.change_image',
            'filer.delete_image',
            'filer.add_thumbnailoption',
            'filer.change_thumbnailoption',
            'filer.delete_thumbnailoption',
            'flatpages.add_flatpage',
            'flatpages.change_flatpage',
            'flatpages.delete_flatpage',
            'sites.add_site',
            'sites.change_site',
            'sites.delete_site'
        ])

    def test_has_perm(self):
        self.assertTrue(has_perm(self.staff_user, "django_tools_test_app.change_permissiontestmodel"))

    def test_has_perm_log(self):
        with LoggingBuffer(name=None, level=logging.ERROR) as log:
            self.assertEqual(has_perm(self.normal_user, "foo.bar1"), False)

        self.assertEqual(
            log.get_messages(),
            "DEBUG:django_tools.permissions:"
            "User normal_test_user has not foo.bar1"
        )

    def test_log_user_permissions1(self):
        with LoggingBuffer(name=None, level=logging.ERROR) as log:
            log_user_permissions(self.normal_user)

        self.assertEqual(
            log.get_messages(),
            "DEBUG:django_tools.permissions:User 'normal_test_user' has no permission!"
        )

    def test_log_user_permissions2(self):
        with LoggingBuffer(name=None, level=logging.ERROR) as log:
            log_user_permissions(self.staff_user)

        messages = [line.strip() for line in log.get_messages().splitlines()]
        pprint.pprint(messages)

        self.assertEqual(
            messages,
            [
                "DEBUG:django_tools.permissions:User 'staff_test_user' has permissions:",
                "* django_tools_test_app.add_permissiontestmodel",
                "* django_tools_test_app.change_permissiontestmodel",
                "* django_tools_test_app.delete_permissiontestmodel",
                "* django_tools_test_app.extra_permission"
            ]
        )

    def test_log_group_permissions1(self):
        with LoggingBuffer(name=None, level=logging.ERROR) as log:
            log_group_permissions(self.normal_group)

        self.assertEqual(
            log.get_messages(),
            "DEBUG:django_tools.permissions:User group 'Normal User Group' has no permission!"
        )

    def test_log_group_permissions2(self):
        with LoggingBuffer(name=None, level=logging.ERROR) as log:
            log_group_permissions(self.staff_group)

        messages = [line.strip() for line in log.get_messages().splitlines()]
        pprint.pprint(messages)

        self.assertEqual(
            messages,
            [
                "DEBUG:django_tools.permissions:User group 'Staff User Group' has permissions:",
                "* django_tools_test_app.add_permissiontestmodel",
                "* django_tools_test_app.change_permissiontestmodel",
                "* django_tools_test_app.delete_permissiontestmodel",
                "* django_tools_test_app.extra_permission"
            ]
        )

    def test_superuser_check(self):
        self.assertTrue(
            check_permission(
                self.superuser,
                permission="superuser check ignores this completely!",
            )
        )

    def test_has_no_extra_permission(self):
        self.assertFalse(
            self.instance.has_extra_permission_permission(
                user=self.normal_user,
                raise_exception=False
            )
        )

    def test_has_extra_permission(self):
        self.assertTrue(
            self.instance.has_extra_permission_permission(
                user=self.staff_user,
                raise_exception=False
            )
        )

    def test_has_default_permissions(self):
        self.assertTrue(self.instance.has_add_permission(user=self.staff_user))
        self.assertTrue(self.instance.has_change_permission(user=self.staff_user))
        self.assertTrue(self.instance.has_delete_permission(user=self.staff_user))

    #-------------------------------------------------------------------------

    def test_add_app_permissions(self):
        with LoggingBuffer(name=None, level=logging.ERROR) as log:
            add_app_permissions(
                permission_obj=self.normal_group,
                app_label="django_tools_test_app"
            )

        self.assertEqual(
            log.get_messages(),
            "DEBUG:django_tools.permissions:Add 10 permissions from app 'django_tools_test_app'"
        )

        permissions = self.normal_group.permissions.all()
        permissions = permissions2list(permissions)
        pprint.pprint(permissions)
        self.assertEqual(permissions, [
            'django_tools_test_app.add_limittousergroupstestmodel',
            'django_tools_test_app.change_limittousergroupstestmodel',
            'django_tools_test_app.delete_limittousergroupstestmodel',
            'django_tools_test_app.add_permissiontestmodel',
            'django_tools_test_app.change_permissiontestmodel',
            'django_tools_test_app.delete_permissiontestmodel',
            'django_tools_test_app.extra_permission',
            'django_tools_test_app.add_simpleparlermodel',
            'django_tools_test_app.change_simpleparlermodel',
            'django_tools_test_app.delete_simpleparlermodel'
        ])

    #-------------------------------------------------------------------------

    def test_get_filtered_permissions_without_any_filter(self):
        permissions = permissions2list(
            get_filtered_permissions() # without any filter -> we get all existing permissions
        )
        permissions.sort()
        pprint.pprint(permissions)

        all_permissions = permissions2list(Permission.objects.all())
        all_permissions.sort()

        self.assertEqual(permissions, all_permissions)

    def test_get_filtered_permissions(self):
        permissions = get_filtered_permissions(
            exclude_app_labels=("easy_thumbnails", "filer"),
            exclude_models=(LimitToUsergroupsTestModel, PermissionTestModel),
            exclude_codenames=("delete_group", "delete_user"),
            exclude_permissions=(
                (ContentType, "add_contenttype"),
                (ContentType, "delete_contenttype"),
            )
        )
        permissions = permissions2list(permissions)
        pprint.pprint(permissions)
        self.assertEqual(permissions, [
            'admin.add_logentry',
            'admin.change_logentry',
            'admin.delete_logentry',
            'auth.add_group',
            'auth.change_group',
            'auth.add_permission',
            'auth.change_permission',
            'auth.delete_permission',
            'auth.add_user',
            'auth.change_user',
            'contenttypes.change_contenttype',
            'django_tools_test_app.add_simpleparlermodel',
            'django_tools_test_app.change_simpleparlermodel',
            'django_tools_test_app.delete_simpleparlermodel',
            'flatpages.add_flatpage',
            'flatpages.change_flatpage',
            'flatpages.delete_flatpage',
            'sessions.add_session',
            'sessions.change_session',
            'sessions.delete_session',
            'sites.add_site',
            'sites.change_site',
            'sites.delete_site'
        ])

    def test_pprint_filtered_permissions_wrong_arguments(self):
        with self.assertRaises(AssertionError) as cm:
            pprint_filtered_permissions(["foo", "bar"])

        self.assert_exception_startswith(cm, "List must contain auth.models.Permission instances!")

    def test_pprint_filtered_permissions(self):
        permissions = get_filtered_permissions(
            exclude_app_labels=("easy_thumbnails", "filer"),
            exclude_actions=("delete",),
            exclude_models=(LimitToUsergroupsTestModel, PermissionTestModel),
            exclude_codenames=("change_group", "change_user"),
            exclude_permissions=(
                (ContentType, "add_contenttype"),
                (ContentType, "delete_contenttype"),
            )
        )
        with StdoutStderrBuffer() as buffer:
            pprint_filtered_permissions(permissions)

        output = buffer.get_output()
        print(output)
        self.assertEqual_dedent(output, """
            [*] admin.add_logentry
            [*] admin.change_logentry
            [ ] admin.delete_logentry
            [*] auth.add_group
            [ ] auth.change_group
            [ ] auth.delete_group
            [*] auth.add_permission
            [*] auth.change_permission
            [ ] auth.delete_permission
            [*] auth.add_user
            [ ] auth.change_user
            [ ] auth.delete_user
            [ ] contenttypes.add_contenttype
            [*] contenttypes.change_contenttype
            [ ] contenttypes.delete_contenttype
            [ ] django_tools_test_app.add_limittousergroupstestmodel
            [ ] django_tools_test_app.change_limittousergroupstestmodel
            [ ] django_tools_test_app.delete_limittousergroupstestmodel
            [ ] django_tools_test_app.add_permissiontestmodel
            [ ] django_tools_test_app.change_permissiontestmodel
            [ ] django_tools_test_app.delete_permissiontestmodel
            [ ] django_tools_test_app.extra_permission
            [*] django_tools_test_app.add_simpleparlermodel
            [*] django_tools_test_app.change_simpleparlermodel
            [ ] django_tools_test_app.delete_simpleparlermodel
            [ ] easy_thumbnails.add_source
            [ ] easy_thumbnails.change_source
            [ ] easy_thumbnails.delete_source
            [ ] easy_thumbnails.add_thumbnail
            [ ] easy_thumbnails.change_thumbnail
            [ ] easy_thumbnails.delete_thumbnail
            [ ] easy_thumbnails.add_thumbnaildimensions
            [ ] easy_thumbnails.change_thumbnaildimensions
            [ ] easy_thumbnails.delete_thumbnaildimensions
            [ ] filer.add_clipboard
            [ ] filer.change_clipboard
            [ ] filer.delete_clipboard
            [ ] filer.add_clipboarditem
            [ ] filer.change_clipboarditem
            [ ] filer.delete_clipboarditem
            [ ] filer.add_file
            [ ] filer.change_file
            [ ] filer.delete_file
            [ ] filer.add_folder
            [ ] filer.can_use_directory_listing
            [ ] filer.change_folder
            [ ] filer.delete_folder
            [ ] filer.add_folderpermission
            [ ] filer.change_folderpermission
            [ ] filer.delete_folderpermission
            [ ] filer.add_image
            [ ] filer.change_image
            [ ] filer.delete_image
            [ ] filer.add_thumbnailoption
            [ ] filer.change_thumbnailoption
            [ ] filer.delete_thumbnailoption
            [*] flatpages.add_flatpage
            [*] flatpages.change_flatpage
            [ ] flatpages.delete_flatpage
            [*] sessions.add_session
            [*] sessions.change_session
            [ ] sessions.delete_session
            [*] sites.add_site
            [*] sites.change_site
            [ ] sites.delete_site
        """)
