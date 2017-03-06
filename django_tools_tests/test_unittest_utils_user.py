# coding: utf-8

"""
    test django_tools.unittest_utils.user stuff
"""

from __future__ import unicode_literals

import warnings

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.contrib.auth.models import Group

from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import create_user, get_super_user


class TestUserUtils(BaseTestCase):

    def test_create_user(self):
        user1 = create_user(username="foo", password="bar")
        user2 = self.UserModel.objects.get(username="foo")

        self.assertEqual(user1.pk, user2.pk)
        self.assertEqual(user1, user2)

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
        self.assertEqual(user.email, "foo@bar.tld")

    def test_groups(self):
        group1 = Group.objects.create(name="Group 1")
        group2 = Group.objects.create(name="Group 2")
        create_user(username="foo", password="foo", groups=(group1, group2))
        user = self.UserModel.objects.get(username="foo")
        groups = user.groups.values_list('pk', 'name')
        self.assertEqual(list(groups), [(1, 'Group 1'), (2, 'Group 2')])

    def test_encrypted_password(self):
        user1 = create_user(username="foo1", password="bar")
        encrypted_password = user1.password
        create_user(username="foo2", encrypted_password=encrypted_password)
        user2 = self.UserModel.objects.get(username="foo2")
        self.assertEqual(user2.password, encrypted_password)

    def test_get_super_user(self):
        create_user(username="foo", password="foo")
        user2 = create_user(username="bar", password="bar", is_superuser=True)
        user3 = get_super_user()

        self.assertEqual(user2.pk, user3.pk)
        self.assertEqual(user2, user3)
        self.assertTrue(user3.is_superuser)

    def test_old_api(self):
        self.assertEqual(self.UserModel.objects.count(), 0)

        userdata = self.TEST_USERS["normal"]
        with warnings.catch_warnings(record=True) as w:

            self.create_user(verbosity=0, **userdata)

            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, FutureWarning))

        self.assertEqual(self.UserModel.objects.count(), 1)
