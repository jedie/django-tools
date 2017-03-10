# coding: utf-8

"""
    permission helpers
    ~~~~~~~~~~~~~~~~~~

    create 03.03.2017 by Jens Diemer
"""


from __future__ import unicode_literals, absolute_import, print_function

import logging

from django.contrib.auth.models import Permission, Group
from django.contrib.admin.sites import site
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied


log = logging.getLogger(__name__)


def add_permissions(permission_obj, permissions):
    """
    Add permissions

    e.g.:
        group = Group.objects.create(name="Foobar Group")
        permissions=(
            (YourModelClass, "the_permission_string"),
        )
        add_permissions(permission_obj=group, permissions=permissions)
    """
    for model_class, codename in permissions:
        content_type = ContentType.objects.get_for_model(model_class)
        try:
            permission = Permission.objects.get(
                content_type=content_type, codename=codename
            )
        except Permission.DoesNotExist:
            raise Permission.DoesNotExist(
                "Permission '%s.%s' doesn't exists!" % (content_type,codename)
            )
        permission_obj.permissions.add(permission)


def create_permission(permission, name, model):
    """
    Create Premission.

    :param permission: String
    :param name: verbose permission name as String
    :param model: model class
    :return: created permission instance

    e.g.:
        create_permission(
            permission="BlogModel.publish",
            name="Can publish blog article",
            model=BlogModel
        )
    """
    model_name, codename = permission.split(".")
    if model_name != model.__name__.lower():
        raise AssertionError(
            "Given permission %r doesn't start with model name %r!" % (
                permission, model.__name__
        ))

    content_type = ContentType.objects.get_for_model(model)

    permission, created = Permission.objects.get_or_create(
        codename=codename, name=name, content_type=content_type
    )
    if created:
        log.debug('\t* Permission "%s" created.\n' % permission.codename)
    else:
        log.debug('\t* Permission "%s" already exists, ok.\n' % permission.codename)
    return permission


def permissions2list(permissions):
    """
    e.g.:

        permissions = our_user_group.permissions.all()
        permissions = permissions2list(permissions)
        pprint.pprint(permissions)
        ['auth.user.add_user',
         'auth.user.change_user',
         'auth.user.delete_user']
    """
    permissions = [
        ".".join([p.content_type.app_label, p.content_type.model, p.codename])
        for p in permissions
    ]
    permissions.sort()
    return permissions


def log_user_permissions(user, log_callable=None):
    """
    Helper to log all existing user permissions.

    e.g.:
        from django_tools.permissions import log_group_permissions
        log = logging.getLogger(__name__)

        log_user_permissions(the_user_instance, log_callable=log.debug)
    """
    if log_callable is None:
        log_callable = log.debug

    permissions = "\n".join(["* %-75s" % p for p in user.get_all_permissions()])
    log_callable('%s has permissions:\n%s', user.username, permissions)


def log_group_permissions(group, log_callable=None):
    """
    Helper to log all existing user group permissions.

    e.g.:
        from django_tools.permissions import log_group_permissions
        log = logging.getLogger(__name__)

        log_group_permissions(user_group_instance, log_callable=log.debug)
    """
    if log_callable is None:
        log_callable = log.debug

    permissions = "\n".join(["* %-75s %s" % (p, p.codename) for p in group.permissions.all()])
    log_callable('%s group permissions:\n%s', group.name, permissions)


def get_admin_permissions():
    """
    :return: list of Permission instances for models that are registered in the admin
    """
    # Create a content type list of all models that are registered in the admin
    admin_content_types = []
    for model in site._registry.keys():
        content_type = ContentType.objects.get_for_model(model)
        admin_content_types.append(content_type)

    # Add all permissions for all admin models:
    permissions = Permission.objects.all()
    permissions = permissions.filter(content_type__in=admin_content_types)
    return permissions


def add_app_permissions(permission_obj, app_label):
    """
    Add all permission from one django app to the given object.
    e.g.:
        add_app_permissions(permission_obj=user_group_instance, app_label="filer")
    """
    content_types = ContentType.objects.filter(app_label = app_label)

    log.debug("Add %i permissions from app %r" % (content_types.count(), app_label))

    permissions = Permission.objects.filter(content_type__in=content_types)
    for permission in permissions:
        permission_obj.permissions.add(permission)


def check_permission(user, permission, raise_exception=True):
    """
    Check if given user has the given permission

    :param user: django user model instance
    :param permission: string e.g.: 'auth.user.add_user'
    :param raise_exception: raise PermissionDenied if user has not the permission
    :return: bool if user has permission
    """
    if user.is_superuser:
        log.debug("Don't check permissions for superuser, ok.")
        return True

    if user.has_perm(permission):
        log.debug('User "%s" has permission "%s"', user, permission)
        return True

    if raise_exception:
        log.error(
            'User "%s" has not permission "%s" -> raise PermissionDenied!',
            user, permission
        )
        raise PermissionDenied
    else:
        log.error('User "%s" has not permission "%s"', user, permission)
        return False


def has_perm(user, permission):
    """
    Verbose check if user has permission:
    Create log entry if user has not the permission
    """
    if not user.has_perm(permission):
        log.debug('User %s has not %s', user, permission)
        return False
    return True

