# coding:utf-8

"""
    Limit to usergroups
    ~~~~~~~~~~~~~~~~~~~

    Helper to limit something to:
        * for everyone (anonymous users)
        * for staff users
        * for superusers
        * for a user group

    In forms you will get a select field with:
        * anonymous users
        * staff users
        * superusers
        * ..all existing user groups..


    usage example
    ~~~~~~~~~~~~~

    model.py
    ---------------------------------------------------------------------------
    class FooBar(models.Model):
        permit_edit = limit_to_usergroups.UsergroupsModelField()
        permit_view = limit_to_usergroups.UsergroupsModelField()
    ---------------------------------------------------------------------------

    views.py
    ---------------------------------------------------------------------------
    def view(request):
        queryset = FooBar.objects.all()
        queryset = limit_to_usergroups.filter_permission(queryset, permit_view=request.user)
        ...

    def edit(request, id):
        foo = FooBar.objects.get(id=id)

        if not limit_to_usergroups.has_permission(poll, permit_edit=request.user):
            msg = _("You have no permission to edit this.")
            if settings.DEBUG:
                verbose_limit_name = limit_to_usergroups.get_verbose_limit_name(foo.permit_edit)
                msg += " (Limited to: %s)" % verbose_limit_name
            messages.error(request, msg)
            return HttpResponseRedirect("foobar)
        ...
    ---------------------------------------------------------------------------


    :copyleft: 2011-2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


from django.db import models
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group


def has_permission(item, **kwargs):
    """
    return True/False if use has permission stored in UsergroupsModelField.

    return True, if permission are ok
    return False, if permission are not sufficient.

    e.g.:
        has_permission(poll, permit_vote=request.user)
        has_permission(item, model_field1=user, model_field2=user)
    """
    for attr_name, user in list(kwargs.items()):
        limit_permission_value = getattr(item, attr_name)
        limit_permission_value = int(limit_permission_value)

        if limit_permission_value == UsergroupsModelField.ANONYMOUS_USERS:
            continue

        if user.is_anonymous():
            return False

        if limit_permission_value == UsergroupsModelField.NORMAL_USERS:
            if user.is_authenticated():
                continue
            else:
                return False

        if limit_permission_value == UsergroupsModelField.STAFF_USERS:
            if user.is_staff:
                continue
            else:
                return False

        if limit_permission_value == UsergroupsModelField.SUPERUSERS:
            if user.is_superuser:
                continue
            else:
                return False

        usergroup = Group.objects.get(id=limit_permission_value)
        usergroups = user.groups.all()
        if usergroup not in usergroups:
            return False

    return True



def filter_permission(queryset, **kwargs):
    """
    Filter a given queryset with UsergroupsModelField.

    e.g.:
        queryset = filter_permission(queryset, permit_view=request.user)
        queryset = filter_permission(queryset, model_field1=user, model_field2=user)

    FIXME: Would be nice, if this is a normal QuerySet method
    """
    result = [item for item in queryset if has_permission(item, **kwargs)]
    return result


def get_verbose_limit_name(value):
    """
    Simply convert the integer value of a UsergroupsModelField to his select choice text

    e.g.:
        x = get_verbose_limit_name(-1)
        print(x) # "staff users"
    """
    limit_dict = get_limit_dict()
    return limit_dict[value]


def get_user_groups():
    groups = Group.objects.values_list("id", "name")
    return list(groups)


def get_limit_dict():
    # use unicode() to evaluate ugettext_lazy:
    limit_dict = dict([(k, six.text_type(v)) for k, v in list(UsergroupsModelField.USER_TYPES_DICT.items())])

    groups = get_user_groups()
    limit_dict.update(dict(groups))
    return limit_dict


class UsergroupsModelField(models.IntegerField):
    """
    TODO: Use html select optgroup [1] to group anonymous, staff and superusers
    from user groups
        [1] http://www.w3.org/wiki/HTML/Elements/optgroup
    """
    ANONYMOUS_USERS = 0
    STAFF_USERS = -1
    SUPERUSERS = -2
    NORMAL_USERS = -3

    USER_TYPES_CHOICES = [
        (ANONYMOUS_USERS, _("anonymous users")),
        (NORMAL_USERS, _("normal users")),
        (STAFF_USERS, _("staff users")),
        (SUPERUSERS, _("superusers")),
    ]
    USER_TYPES_DICT = dict(USER_TYPES_CHOICES)

    def __init__(self, *args, **kwargs):
        """
        We added only the static choices here, because we should not access
        the database here (can break unittests)
        In this cases the choices feature of this field is activated, but
        in any case self.get_choices() would be called: There we append
        the user groups
        """
        kwargs["choices"] = self.USER_TYPES_CHOICES

        super(UsergroupsModelField, self).__init__(*args, **kwargs)

    def get_choices(self, *args, **kwargs):
        """
        Built the choices list with the static part and all existing
        user groups from database.
        """
        groups = get_user_groups()
        choices = self.USER_TYPES_CHOICES + list(groups)
        return choices


