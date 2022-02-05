import logging
import pprint

from bx_py_utils.test_utils.snapshot import assert_snapshot, assert_text_snapshot
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.test import override_settings

# https://github.com/jedie/django-tools
from django_tools.permissions import (
    add_app_permissions,
    add_permissions,
    check_permission,
    get_admin_permissions,
    get_filtered_permissions,
    get_permission_by_string,
    has_perm,
    log_group_permissions,
    log_user_permissions,
    permissions2list,
    pprint_filtered_permissions,
)
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import TestUserMixin
from django_tools_test_project.django_tools_test_app.models import (
    LimitToUsergroupsTestModel,
    PermissionTestModel,
)


log = logging.getLogger(__name__)


@override_settings(DEBUG=True)
class TestPermissions(TestUserMixin, BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.extra_permission = get_permission_by_string(
            permission="django_tools_test_app.extra_permission"
        )

        cls.instance = PermissionTestModel.objects.create(foo="bar")

    def setUp(self):
        super().setUp()

        users = User.objects.all()
        usernames = users.values_list("username", flat=True).order_by("username")
        assert tuple(usernames) == ("normal_test_user", "staff_test_user", "superuser")

        self.superuser = self._get_user(usertype="superuser")

        # The "staff user" has some permissions:
        self.staff_user = self._get_user(usertype="staff")
        self.staff_group = Group.objects.create(name="Staff User Group")
        self.staff_group.permissions.add(self.extra_permission)
        self.staff_group.permissions.add(
            get_permission_by_string("django_tools_test_app.add_permissiontestmodel")
        )
        self.staff_group.permissions.add(
            get_permission_by_string("django_tools_test_app.change_permissiontestmodel")
        )
        self.staff_group.permissions.add(
            get_permission_by_string("django_tools_test_app.delete_permissiontestmodel")
        )
        self.staff_user.groups.add(self.staff_group)
        self.staff_user.save()

        # The "normal user" has no permissions:
        self.normal_user = self._get_user(usertype="normal")
        self.normal_group = Group.objects.create(name="Normal User Group")
        self.normal_user.groups.add(self.normal_group)
        self.normal_user.save()

    # -------------------------------------------------------------------------

    def assert_permissiontestmodel(self, permission):
        self.assertIsInstance(permission, Permission)
        self.assertIsInstance(permission.content_type, ContentType)

        assert_pformat_equal(permission.content_type.app_label, "django_tools_test_app")
        assert_pformat_equal(permission.content_type.model, "permissiontestmodel")

    def assert_extra_permission(self, permission):
        self.assert_permissiontestmodel(permission)
        assert_pformat_equal(permission.codename, "extra_permission")

    # -------------------------------------------------------------------------

    def test_setup(self):
        self.assert_extra_permission(self.extra_permission)

        # The "normal user" has no permissions
        assert_pformat_equal(self.normal_user.get_all_permissions(), set())

        # The "staff user" has some permissions
        assert_pformat_equal(
            self.staff_user.get_all_permissions(),
            {
                "django_tools_test_app.extra_permission",
                "django_tools_test_app.add_permissiontestmodel",
                "django_tools_test_app.change_permissiontestmodel",
                "django_tools_test_app.delete_permissiontestmodel",
            },
        )

        all_permissions = [
            f"{entry.content_type.app_label}.{entry.codename}" for entry in Permission.objects.all()
        ]

        # Default mode permissions:
        self.assertIn("django_tools_test_app.add_permissiontestmodel", all_permissions)
        self.assertIn("django_tools_test_app.change_permissiontestmodel", all_permissions)
        self.assertIn("django_tools_test_app.delete_permissiontestmodel", all_permissions)

        # Own permission defined via Meta.permissions:
        self.assertIn("django_tools_test_app.extra_permission", all_permissions)

    # -------------------------------------------------------------------------

    def test_get_default_permissions(self):
        # https://docs.djangoproject.com/en/1.8/ref/models/options/#default-permissions
        permission = get_permission_by_string("django_tools_test_app.add_permissiontestmodel")
        self.assert_permissiontestmodel(permission)
        assert_pformat_equal(permission.codename, "add_permissiontestmodel")

        permission = get_permission_by_string("django_tools_test_app.change_permissiontestmodel")
        self.assert_permissiontestmodel(permission)
        assert_pformat_equal(permission.codename, "change_permissiontestmodel")

        permission = get_permission_by_string("django_tools_test_app.delete_permissiontestmodel")
        self.assert_permissiontestmodel(permission)
        assert_pformat_equal(permission.codename, "delete_permissiontestmodel")

    def test_get_extra_permission(self):
        # https://docs.djangoproject.com/en/1.8/ref/models/options/#permissions
        permission = get_permission_by_string("django_tools_test_app.extra_permission")
        self.assert_extra_permission(permission)

    # -------------------------------------------------------------------------

    def test_get_permission_wrong_format(self):
        with self.assertRaises(PermissionDenied) as cm:
            get_permission_by_string("no_dot_in_string")

        self.assert_exception_startswith(cm, "Wrong permission string format")

    def test_get_permission_wrong_app_label(self):
        with self.assertRaises(PermissionDenied) as cm:
            get_permission_by_string("wrong.foobar")

        self.assert_exception_startswith(
            cm, "App label 'wrong' from permission 'wrong.foobar' doesn't exists!"
        )

    def test_get_permission_wrong_codename(self):
        with self.assertRaises(PermissionDenied) as cm:
            get_permission_by_string("auth.wrong")

        self.assert_exception_startswith(
            cm, "Codename 'wrong' from permission 'auth.wrong' doesn't exists!"
        )

    # -------------------------------------------------------------------------

    def test_add_permissions(self):
        permissions = ((LimitToUsergroupsTestModel, "extra_permission"),)
        add_permissions(permission_obj=self.normal_group, permissions=permissions)

        user = self.refresh_user(self.normal_user)
        assert_pformat_equal(user.get_all_permissions(), {"django_tools_test_app.extra_permission"})

    def test_check_permission_error_without_exception(self):
        self.assertFalse(
            check_permission(
                self.normal_user, "django_tools_test_app.extra_permission", raise_exception=False
            )
        )

    def test_check_permission_error_with_exception(self):
        with self.assertRaises(PermissionDenied) as cm:
            check_permission(self.normal_user, "django_tools_test_app.extra_permission")

        self.assertFalse(hasattr(cm, "args"))  # No error message

    def test_check_permission_existing(self):
        self.assertTrue(check_permission(self.staff_user, "django_tools_test_app.extra_permission"))

    # -------------------------------------------------------------------------

    def test_check_permission_wrong_format(self):
        check_permission(self.superuser, "no_dot_in_string")  # superuser can do everything ;)

        with self.assertRaises(PermissionDenied) as cm:
            check_permission(self.staff_user, "no_dot_in_string")

        self.assert_exception_startswith(cm, "Wrong permission string format")

    def test_check_permission_wrong_app_label(self):
        check_permission(self.superuser, "wrong.foobar")  # superuser can do everything ;)

        with self.assertRaises(PermissionDenied) as cm:
            check_permission(self.staff_user, "wrong.foobar")

        self.assert_exception_startswith(
            cm, "App label 'wrong' from permission 'wrong.foobar' doesn't exists!"
        )

    def test_check_permission_wrong_codename(self):
        check_permission(self.superuser, "auth.wrong")  # superuser can do everything ;)

        with self.assertRaises(PermissionDenied) as cm:
            check_permission(self.staff_user, "auth.wrong")

        self.assert_exception_startswith(
            cm, "Codename 'wrong' from permission 'auth.wrong' doesn't exists!"
        )

    def test_get_admin_permissions(self):
        permissions = get_admin_permissions()
        permissions = permissions2list(permissions)
        assert permissions
        assert 'auth.add_user' in permissions
        assert 'django_tools_test_app.change_overwritefilesystemstoragemodel' in permissions
        assert 'django_tools_test_app.extra_permission' in permissions
        assert_snapshot(got=permissions)

    def test_has_perm(self):
        self.assertTrue(
            has_perm(self.staff_user, "django_tools_test_app.change_permissiontestmodel")
        )

    def test_has_perm_log(self):
        with self.assertLogs(logger="django_tools.permissions", level=logging.DEBUG) as log:
            assert_pformat_equal(has_perm(self.normal_user, "foo.bar1"), False)

        assert log.output == [
            "DEBUG:django_tools.permissions:" "User normal_test_user has not foo.bar1"
        ]

    def test_log_user_permissions1(self):
        with self.assertLogs(logger="django_tools.permissions", level=logging.DEBUG) as log:
            log_user_permissions(self.normal_user)

        assert log.output == [
            "DEBUG:django_tools.permissions:User 'normal_test_user' has no permission!"
        ]

    def test_log_user_permissions2(self):
        with self.assertLogs(logger="django_tools.permissions", level=logging.DEBUG) as log:
            log_user_permissions(self.staff_user)

        assert log.output == [
            "DEBUG:django_tools.permissions:User 'staff_test_user' has permissions:\n"
            '* django_tools_test_app.add_permissiontestmodel\n'
            '* django_tools_test_app.change_permissiontestmodel\n'
            '* django_tools_test_app.delete_permissiontestmodel\n'
            '* django_tools_test_app.extra_permission',
        ]

    def test_log_group_permissions1(self):
        with self.assertLogs(logger="django_tools.permissions", level=logging.DEBUG) as log:
            log_group_permissions(self.normal_group)

        assert log.output == [
            "DEBUG:django_tools.permissions:User group 'Normal User Group' has no permission!"
        ]

    def test_log_group_permissions2(self):
        with self.assertLogs(logger="django_tools.permissions", level=logging.DEBUG) as log:
            log_group_permissions(self.staff_group)

        assert log.output == [
            "DEBUG:django_tools.permissions:User group 'Staff User Group' has permissions:\n"
            '* django_tools_test_app.add_permissiontestmodel\n'
            '* django_tools_test_app.change_permissiontestmodel\n'
            '* django_tools_test_app.delete_permissiontestmodel\n'
            '* django_tools_test_app.extra_permission',
        ]

    def test_superuser_check(self):
        self.assertTrue(
            check_permission(self.superuser, permission="superuser check ignores this completely!")
        )

    def test_has_no_extra_permission(self):
        self.assertFalse(
            self.instance.has_extra_permission_permission(
                user=self.normal_user, raise_exception=False
            )
        )

    def test_has_extra_permission(self):
        self.assertTrue(
            self.instance.has_extra_permission_permission(
                user=self.staff_user, raise_exception=False
            )
        )

    def test_has_default_permissions(self):
        self.assertTrue(self.instance.has_add_permission(user=self.staff_user))
        self.assertTrue(self.instance.has_change_permission(user=self.staff_user))
        self.assertTrue(self.instance.has_delete_permission(user=self.staff_user))

    # -------------------------------------------------------------------------

    def test_add_app_permissions(self):
        permissions = self.normal_group.permissions.all()
        permissions = permissions2list(permissions)
        assert_pformat_equal(permissions, [])

        with self.assertLogs(logger='django_tools.permissions', level=logging.DEBUG) as logs:
            add_app_permissions(permission_obj=self.normal_group, app_label='django_tools_test_app')

        assert_pformat_equal(
            logs.output,
            ["DEBUG:django_tools.permissions:Add 25 permissions from app 'django_tools_test_app'"]
        )

        permissions = self.normal_group.permissions.all()
        permissions = permissions2list(permissions)
        assert permissions
        assert 'django_tools_test_app.add_limittousergroupstestmodel' in permissions
        assert 'auth.add_user' not in permissions
        assert_snapshot(got=permissions)

    def test_get_filtered_permissions_without_any_filter(self):
        permissions = sorted(permissions2list(
            get_filtered_permissions()  # without any filter -> we get all existing permissions
        ))
        pprint.pprint(permissions)

        all_permissions = sorted(permissions2list(Permission.objects.all()))

        assert_pformat_equal(permissions, all_permissions)

    def test_get_filtered_permissions(self):
        permissions = get_filtered_permissions(
            exclude_app_labels=('easy_thumbnails', 'filer'),
            exclude_models=(LimitToUsergroupsTestModel, PermissionTestModel),
            exclude_codenames=('delete_group', 'delete_user'),
            exclude_permissions=(
                (ContentType, 'add_contenttype'),
                (ContentType, 'delete_contenttype'),
            ),
        )
        permissions = permissions2list(permissions)
        assert permissions
        assert 'admin.add_logentry' in permissions
        assert 'auth.delete_group' not in permissions
        assert 'filer.add_image' not in permissions
        assert 'contenttypes.change_contenttype' in permissions
        assert 'contenttypes.add_contenttype' not in permissions
        assert_snapshot(got=permissions)

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
            ),
        )
        with StdoutStderrBuffer() as buffer:
            pprint_filtered_permissions(permissions)

        output = buffer.get_output()
        assert '[*] admin.add_logentry' in output
        assert '[ ] admin.delete_logentry' in output
        assert '[ ] filer.add_image' in output
        assert_text_snapshot(got=output)
