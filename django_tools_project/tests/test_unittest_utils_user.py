"""
    test django_tools.unittest_utils.user stuff

    :copyleft: 2017-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from bx_py_utils.test_utils.snapshot import assert_text_snapshot
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.core.management import call_command

# https://github.com/jedie/django-tools
from django_tools.permissions import get_filtered_permissions
from django_tools.unittest_utils.assertments import assert_equal_dedent, assert_pformat_equal
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import (
    TestUserMixin,
    create_user,
    get_or_create_group,
    get_or_create_user,
    get_or_create_user_and_group,
    get_super_user,
)


class TestUserUtils(TestUserMixin, BaseTestCase):
    def test_create_user(self):
        user1 = create_user(username="foo", password="bar")
        user2 = self.UserModel.objects.get(username="foo")

        assert_pformat_equal(user1.pk, user2.pk)
        assert_pformat_equal(user1, user2)

        # check defaults:
        self.assertFalse(user2.is_staff)
        self.assertFalse(user2.is_superuser)

    def test_superuser(self):
        create_user(username="foo", password="bar", is_superuser=True)
        user = self.UserModel.objects.get(username="foo")

        self.assertTrue(user.is_superuser)

        # check defaults:
        self.assertFalse(user.is_staff)

    def test_email(self):
        user = create_user(username="foo", password="foo", email="foo@bar.tld")
        assert_pformat_equal(user.email, "foo@bar.tld")

    def test_groups(self):
        group1 = Group.objects.create(name="Group 1")
        group2 = Group.objects.create(name="Group 2")
        create_user(username="foo", password="foo", groups=(group1, group2))
        user = self.UserModel.objects.get(username="foo")
        groups = user.groups.values_list("pk", "name")
        assert_pformat_equal(list(groups), [(1, "Group 1"), (2, "Group 2")])

    def test_encrypted_password(self):
        user1 = create_user(username="foo1", password="bar")
        encrypted_password = user1.password
        create_user(username="foo2", encrypted_password=encrypted_password)
        user2 = self.UserModel.objects.get(username="foo2")
        assert_pformat_equal(user2.password, encrypted_password)

    def test_get_super_user(self):
        self.UserModel.objects.all().delete()

        create_user(username="foo", password="foo")
        user2 = create_user(username="bar", password="bar", is_superuser=True)
        user3 = get_super_user()

        assert_pformat_equal(user2.pk, user3.pk)
        assert_pformat_equal(user2, user3)
        self.assertTrue(user3.is_superuser)


class TestUserFixtures(TestUserMixin, BaseTestCase):
    def assert_user_fixtures(self):
        users = self.UserModel.objects.all()
        usernames = users.values_list("username", flat=True).order_by("username")
        reference = ("normal_test_user", "staff_test_user", "superuser")
        assert_pformat_equal(tuple(usernames), reference)

    def test_double_creation(self):
        self.assert_user_fixtures()
        self.create_testusers()  # create user a second time
        self.assert_user_fixtures()

    def test_get_or_create_user_and_group(self):
        superuser = self.UserModel.objects.filter(is_superuser=True, is_active=True)[0]
        encrypted_password = superuser.password

        test_user = get_or_create_user_and_group(
            username="testuser",
            groupname="testgroup",
            permissions=get_filtered_permissions(
                exclude_app_labels=("admin", "sites"),
                exclude_models=(Session,),
                exclude_codenames=("delete_user", "delete_group"),
                exclude_permissions=((ContentType, "add_contenttype"), (ContentType, "delete_contenttype")),
            ),
            encrypted_password=encrypted_password,
        )

        with StdoutStderrBuffer() as buff:
            call_command("permission_info", "testuser")
        output = buff.get_output()

        assert 'Display effective user permissions' in output
        assert 'is_active    : yes' in output
        assert '[ ] admin.add_logentry' in output
        assert '[*] auth.add_group' in output
        assert '[ ] sites.view_site' in output

        assert_text_snapshot(got=output)

        assert_pformat_equal(test_user.password, encrypted_password)

    def test_remove_obsolete_permissions(self):
        superuser = self.UserModel.objects.filter(is_superuser=True, is_active=True)[0]
        encrypted_password = superuser.password

        # Create with more permissions:
        get_or_create_user_and_group(
            username="testuser",
            groupname="testgroup",
            permissions=get_filtered_permissions(
                exclude_app_labels=("admin",),
                exclude_codenames=("delete_group",),
                exclude_permissions=((ContentType, "delete_contenttype"),),
            ),
            encrypted_password=encrypted_password,
        )

        with StdoutStderrBuffer() as buff:
            get_or_create_user_and_group(
                username="testuser",
                groupname="testgroup",
                permissions=get_filtered_permissions(
                    exclude_app_labels=("admin", "sites"),
                    exclude_models=(Session,),
                    exclude_codenames=("delete_user", "delete_group"),
                    exclude_permissions=((ContentType, "add_contenttype"), (ContentType, "delete_contenttype")),
                ),
                encrypted_password=encrypted_password,
            )
        output = buff.get_output()
        print(output)
        assert_equal_dedent(
            output,
            """
            Check 'admin'
            Check 'sites'
            remove permission: auth | user | Can delete user
            remove permission: contenttypes | content type | Can add content type
            remove permission: sessions | session | Can add session
            remove permission: sessions | session | Can change session
            remove permission: sessions | session | Can delete session
            remove permission: sessions | session | Can view session
            remove permission: sites | site | Can add site
            remove permission: sites | site | Can change site
            remove permission: sites | site | Can delete site
            remove permission: sites | site | Can view site
            Add 86 permissions to 'testgroup'
            Group testgroup has 86 permissions
            """,
        )

    def test_update_existing_user(self):
        superuser = self.UserModel.objects.filter(is_superuser=True, is_active=True)[0]
        encrypted_password = superuser.password

        group1, created = get_or_create_group(groupname="group1", permissions=())
        self.assertTrue(created)

        user, created = get_or_create_user(username="foo", group=group1, encrypted_password=encrypted_password)
        self.assertTrue(created)

        assert_pformat_equal(list(self.UserModel.objects.get(username="foo").groups.all()), [group1])

        # Update user and attach group2:

        group2, created = get_or_create_group(groupname="group2", permissions=())
        self.assertTrue(created)

        user, created = get_or_create_user(username="foo", group=group2, encrypted_password=encrypted_password)
        self.assertFalse(created)

        assert_pformat_equal(list(self.UserModel.objects.get(username="foo").groups.all()), [group2])
