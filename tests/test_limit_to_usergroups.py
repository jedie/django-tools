# coding: utf-8

"""
    Test limit to usergroups
    ~~~~~~~~~~~~~~~~~~~~~~~~
    
    Unittests for limit_to_usergroups.py, see:
    https://github.com/jedie/django-tools/blob/master/django_tools/limit_to_usergroups.py
    
    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import unittest

if __name__ == "__main__":
    # run unittest directly
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django_tools_test_project.test_settings"

from django.test import TestCase
from django.core import management
from django.contrib.auth.models import Group, AnonymousUser

from django_tools import limit_to_usergroups
from django_tools.limit_to_usergroups import get_verbose_limit_name,\
    has_permission
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools_test_project.django_tools_test_app.models import LimitToUsergroupsTestModel


class LimitToUsergroupsTest1(TestCase):
    def setUp(self):
        self.instance = LimitToUsergroupsTestModel.objects.create(
            permit_edit = limit_to_usergroups.UsergroupsModelField.SUPERUSERS,
            permit_view = limit_to_usergroups.UsergroupsModelField.ANONYMOUS_USERS,
        )

    def test_basic(self):
        self.assertEqual(
            self.instance.permit_edit,
            limit_to_usergroups.UsergroupsModelField.SUPERUSERS
        )
        self.assertEqual(
            self.instance.permit_view,
            limit_to_usergroups.UsergroupsModelField.ANONYMOUS_USERS
        )


class LimitToUsergroupsTest2(BaseTestCase, TestCase):
    def _pre_setup(self):
        super(LimitToUsergroupsTest2, self)._pre_setup()
        self.create_testusers()
        
    def setUp(self):
        self.user1 = self.login(usertype="staff")
        
        self.instance1 = LimitToUsergroupsTestModel.objects.create(
            permit_edit = limit_to_usergroups.UsergroupsModelField.STAFF_USERS,
            permit_view = limit_to_usergroups.UsergroupsModelField.ANONYMOUS_USERS,
        )
        self.user_group = Group.objects.create(name="user group 1")

        self.instance2 = LimitToUsergroupsTestModel.objects.create(
            permit_edit = self.user_group.pk,
            permit_view = limit_to_usergroups.UsergroupsModelField.NORMAL_USERS,
        )
        
    def test_filter_permission1(self):
        queryset = LimitToUsergroupsTestModel.objects.all()
        
        # Anonymous can view all
        items = limit_to_usergroups.filter_permission(
            queryset, permit_view=self.user1
        )
        self.assertEqual(len(items), 2)
        
    def test_filter_permission2(self):
        queryset = LimitToUsergroupsTestModel.objects.all()
        
        # edit only for staff or users in the right user group
        items = limit_to_usergroups.filter_permission(
            queryset, permit_edit=self.user1
        )
        self.assertEqual(len(items), 1)
        
    def test_filter_permission3(self):
        queryset = LimitToUsergroupsTestModel.objects.all()
        
        # Check if he is in the user group
        self.user1.groups.add(self.user_group)
        self.user1.save()
        items = limit_to_usergroups.filter_permission(
            queryset, permit_edit=self.user1
        )
        self.assertEqual(len(items), 2)

    def test_has_permission1(self):
        anonymous = AnonymousUser()
        
        self.assertTrue(
            has_permission(self.instance1, permit_view=anonymous)
        )
        self.assertFalse(
            has_permission(self.instance1, permit_edit=anonymous)
        )
        
    def test_has_permission2(self):
        anonymous = AnonymousUser()
        
        self.assertFalse(
            has_permission(self.instance2, permit_view=anonymous, permit_edit=anonymous)
        )
        
    def test_has_permission3(self):
        user = self.login(usertype="normal")
        self.assertFalse(
            has_permission(self.instance2, permit_view=user, permit_edit=user)
        )     
        user.groups.add(self.user_group)
        user.save()
        self.assertTrue(
            has_permission(self.instance2, permit_view=user, permit_edit=user)
        )

    def test_verbose_limit_name1(self):
        self.assertEqual(
            get_verbose_limit_name(limit_to_usergroups.UsergroupsModelField.STAFF_USERS),
            'staff users'
        )

    def test_verbose_limit_name2(self):
        self.assertEqual(
            get_verbose_limit_name(self.user_group.pk),
            'user group 1'
        )


if __name__ == "__main__":
    # Run this unittest directly
    management.call_command('test',
        "django_tools.LimitToUsergroupsTest1",
        "django_tools.LimitToUsergroupsTest2",
        verbosity=2,
#        failfast=True
    )
    unittest.main()

