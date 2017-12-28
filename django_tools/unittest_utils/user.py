# coding: utf-8

from __future__ import unicode_literals

import logging

import sys

import pytest
from django.contrib import auth

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

log = logging.getLogger(__name__)


def create_user(
    username, password=None, email="",
    is_staff=False, is_superuser=False,
    encrypted_password=None, groups=None,
    update_existing=False
    ):
    """
    Create a user and return the instance.

    :param password: Plain Text password
    :param encrypted_password: Hashed password (e.g. cloned vom other user)
    :param groups: List of user group names
    :return: created user instance
    """
    if password is None and encrypted_password is None:
        raise RuntimeError("'password' or 'encrypted_password' needed.")

    User=get_user_model()

    user = None
    if update_existing:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        else:
            created=False

    if user is None:
        # Create user with origin form to validate username:
        user_form_data={
            "username": username,
            "password1": password,
            "password2": password,
        }

        if password is None:
            # encrypted_password set later!
            # Set something, to run validation.
            user_form_data["password1"] = user_form_data["password2"] = "A temp password!"

        user_form = UserCreationForm(user_form_data)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            created = True
        else:
            raise ValidationError("%s" % user_form.errors)

    user.email = email
    user.is_staff = is_staff
    user.is_superuser = is_superuser

    if encrypted_password:
        log.critical("Set encrypted user password, ok.")
        user.password = encrypted_password
    elif password:
        user.set_password(password)
    else:
        raise RuntimeError # should never happen, see above ;)

    user.save()

    if groups:
        for group_name in groups:
            try:
                user_group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                raise RuntimeError('User group "%s" not found!' % group_name)
            user.groups.add(user_group)

    if created:
        log.debug("Create new user %r account" % user)
    else:
        log.debug("Update existing %r account" % user)

    return user


def get_super_user():
    """
    :return: the first 'superuser'
    """
    User=get_user_model()
    try:
        super_user = User.objects.filter(is_superuser=True)[0]
    except (User.DoesNotExist, IndexError):
        log.error("Can't get a superuser. Please create first!")
        raise RuntimeError("No superuser")
    return super_user


def get_or_create_user(username, group, encrypted_password):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = create_user(
            username=username,
            groups=(group,),
            is_staff=True,
            is_superuser=False,
            encrypted_password=encrypted_password,
        )
        created = True
    else:
        created = False

    user.groups=(group,)
    user.is_staff=True
    user.is_superuser=False
    user.save()

    return user, created


def get_or_create_group(groupname, permissions):
    group, created = Group.objects.get_or_create(name=groupname)

    for permission in group.permissions.all():
        if permission not in permissions:
            print("remove permission:", permission)
            group.permissions.remove(permission)

    print("Add %i permissions to %r" % (len(permissions), groupname))
    for permission in permissions:
        group.permissions.add(permission)

    existing_permission_count = group.permissions.all().count()
    print("Group %s has %i permissions" % (groupname, existing_permission_count))
    assert len(permissions) == existing_permission_count, "Wrong permission count: %i != %i" % (
        existing_permission_count, len(permissions)
    )

    return group, created


def get_or_create_user_and_group(username, groupname, permissions, encrypted_password):
    """
    * Creates a user group if not exists
    * add given permissions to user group
    * create user if not exists
    * adds user into user group

    e.g.:
        from django_tools.permissions import get_filtered_permissions
        from django_tools.unittest_utils.user import get_or_create_user_and_group

        superuser = User.objects.filter(is_superuser=True, is_active=True)[0]
        encrypted_password = superuser.password

        test_user = get_or_create_user_and_group(
            username="testuser",
            groupname="testgroup",
            permissions=get_filtered_permissions(
                exclude_app_labels=("auth", "sites"),
                exclude_models=(),
                exclude_permissions=(),
            ),
            encrypted_password=encrypted_password
        )
    """
    log.info("Create user group %s and add %i permissions...", groupname, len(permissions))
    group, created = get_or_create_group(groupname, permissions)
    if created:
        log.debug("User group '%s' created.", groupname)
    else:
        log.debug("Use existing user group '%s', ok.", groupname)

    log.info("Create user '%s'...", username)
    user, created = get_or_create_user(username, group, encrypted_password)
    if created:
        log.debug("User '%s' created.", username)
    else:
        log.debug("User '%s' already exists, ok.", username)

    return user


class TestUserMixin:
    """
    Important: Test user will only be created, if django TestCase is used!
    e.g:

    from django.test.testcases import TestCase

    class FooBarTestCase(TestUserMixin, TestCase):
        def test...

    """
    TEST_USERS = {
        "superuser": {
            "username": "superuser",
            "email": "superuser@example.org",
            "password": "superuser_password",
            "is_staff": True,
            "is_superuser": True,
        },
        "staff": {
            "username": "staff_test_user",
            "email": "staff_test_user@example.org",
            "password": "staff_test_user_password",
            "is_staff": True,
            "is_superuser": False,
        },
        "normal": {
            "username": "normal_test_user",
            "email": "normal_test_user@example.org",
            "password": "normal_test_user_password",
            "is_staff": False,
            "is_superuser": False,
        },
    }


    @classmethod
    def setUpClass(cls):
        super(TestUserMixin, cls).setUpClass()
        cls.UserModel = auth.get_user_model()

    @classmethod
    def setUpTestData(cls):
        super(TestUserMixin, cls).setUpTestData()
        cls.create_testusers(cls)

    def create_testusers(self):
        """
        Create all available testusers and UserProfiles
        """
        for user_data in self.TEST_USERS.values():
            user = create_user(update_existing=True, **user_data)
            log.debug("Test user %s created." % user)

    def get_userdata(self, usertype):
        """ return userdata from self.TEST_USERS for the given usertype """
        try:
            return self.TEST_USERS[usertype]
        except KeyError as err:
            etype, evalue, etb = sys.exc_info()
            evalue = etype(
                'Wrong usetype %s! Existing usertypes are: %s' % (err, ", ".join(list(self.TEST_USERS.keys())))
            )
            raise etype(evalue).with_traceback(etb)

    def _get_user(self, usertype):
        """ return User model instance for the given usertype"""
        test_user = self.get_userdata(usertype)
        return self.UserModel.objects.get(username=test_user["username"])

    def login(self, usertype):
        """
        Login the user defined in self.TEST_USERS
        return User model instance
        """
        test_user = self.get_userdata(usertype)

        count = self.UserModel.objects.filter(username=test_user["username"]).count()
        self.assertNotEqual(count, 0, "You have to call self.create_testusers() first!")
        self.assertEqual(count, 1)

        ok = self.client.login(username=test_user["username"],
                               password=test_user["password"])
        self.assertTrue(ok, 'Can\'t login test user "%s"!' % usertype)
        return self._get_user(usertype)

    def add_user_permissions(self, user, permissions):
        """
        add permissions to the given user instance.
        permissions e.g.: ("AppLabel.add_Modelname", "auth.change_user")
        """
        assert isinstance(permissions, (list, tuple))
        for permission in permissions:
            # permission, e.g: blog.add_blogentry
            app_label, permission_codename = permission.split(".", 1)
            model_name = permission_codename.split("_", 1)[1]

            try:
                content_type = ContentType.objects.get(app_label=app_label, model=model_name)
            except ContentType.DoesNotExist:
                etype, evalue, etb = sys.exc_info()
                evalue = etype('Can\'t get ContentType for app "%s" and model "%s": %s' % (
                    app_label, model_name, evalue
                ))
                raise etype(evalue).with_traceback(etb)

            perm = Permission.objects.get(content_type=content_type, codename=permission_codename)
            user.user_permissions.add(perm)
            user.save()

        self.assertTrue(user.has_perms(permissions))

    def refresh_user(self, user):
        """
        Return a fresh User model instance from DB.
        Note: Using "user.refresh_from_db()" will not help in every case!
        e.g.: Add new permission on user group and check the added one.
        """
        return self.UserModel.objects.get(pk=user.pk)
