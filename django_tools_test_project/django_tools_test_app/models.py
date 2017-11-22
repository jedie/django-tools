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
    def has_extra_permission_permission(cls, user, raise_exception=True):
        permission = cls.extra_permission_name(action="extra_permission")
        return check_permission(user, permission, raise_exception)

    class Meta:
        # https://docs.djangoproject.com/en/1.8/ref/models/options/#permissions
        permissions = (
            ("extra_permission", "Extra permission"),
        )
