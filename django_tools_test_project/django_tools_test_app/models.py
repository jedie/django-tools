# coding: utf-8

"""
    django-tools test models
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012-2017 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


from django.db import models
from django_tools import limit_to_usergroups
from django_tools.permissions import ModelPermissionMixin, check_permission


class LimitToUsergroupsTestModel(models.Model):
    permit_edit = limit_to_usergroups.UsergroupsModelField()
    permit_view = limit_to_usergroups.UsergroupsModelField()


class PermissionTestModel(ModelPermissionMixin, models.Model):
    foo = models.CharField(max_length=127)

    @classmethod
    def has_extra_permission1_permission(cls, user, raise_exception=True):
        permission = cls.permission_name(action="extra_permission1")
        return check_permission(user, permission, raise_exception)

    class Meta:
        permissions = (
            ("extra_permission1", "Extra permission 1"),
            ("extra_permission2", "Extra permission 2"),
        )
