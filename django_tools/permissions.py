# coding: utf-8

"""
    permission helpers
    ~~~~~~~~~~~~~~~~~~

    create 03.03.2017 by Jens Diemer
"""


from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.conf import settings
from django.contrib.admin.sites import site
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

log = logging.getLogger(__name__)


def pformat_permission(permission):
    """
    Generate the permission string in the same format as user.has_perm() argument:
        "<appname>.<codename>"
    """
    assert isinstance(permission, Permission), "No auth.models.Permission instance!"
    return "%s.%s" % (permission.content_type.app_label, permission.codename)


def get_permission(app_label, codename):
    try:
        perm_obj = Permission.objects.all().get(
            content_type__app_label=app_label,
            codename=codename
        )
    except Permission.DoesNotExist as err:
        log.exception("Error get permission '%s.%s':%s", app_label, codename, err)

        content_types = ContentType.objects.all().filter(app_label=app_label)
        if content_types.count() == 0:
            qs = ContentType.objects.all().values_list("app_label", flat=True).order_by("app_label")
            try:
                app_lables = ", ".join(qs.distinct("app_label"))
            except NotImplementedError:
                # e.g.: sqlite has no distinct
                app_lables = ", ".join(set(qs))
            raise PermissionDenied(
                (
                    "App label '%s' from permission '%s.%s' doesn't exists!"
                    " All existing labels are: %s"
                ) % (app_label, app_label, codename, app_lables)
            )
        qs = Permission.objects.all().filter(content_type__in=content_types)
        if qs.filter(codename=codename).count() == 0:
            codenames = qs.values_list("codename", flat=True).order_by("codename")
            raise PermissionDenied(
                (
                    "Codename '%s' from permission '%s.%s' doesn't exists!"
                    " All existing codenames are: %s"
                ) % (codename, app_label, codename, ", ".join(codenames))
            )
    else:
        return perm_obj


def get_permission_by_string(permission):
    try:
        app_label, codename = permission.split(".")
    except ValueError as err:
        raise PermissionDenied(
            "Wrong permission string format '%s': %s" % (permission, err)
        )
    return get_permission(app_label, codename)


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
        app_label = content_type.app_label
        permission = get_permission(app_label, codename)
        permission_obj.permissions.add(permission)


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
    permissions = [pformat_permission(permission) for permission in permissions]
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

    permissions = sorted(user.get_all_permissions()) # A string list!

    if not permissions:
        log_callable("User '%s' has no permission!", user.username)
    else:
        permissions = "\n".join(["* %s" % p for p in permissions])
        log_callable("User '%s' has permissions:\n%s", user.username, permissions)


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

    permissions = group.permissions.all().order_by("content_type", "codename")
    if not permissions:
        log_callable("User group '%s' has no permission!", group.name)
    else:
        permissions = "\n".join([
            "* %s" % pformat_permission(permission)
            for permission in permissions
        ])
        log_callable("User group '%s' has permissions:\n%s", group.name, permissions)


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
    permissions = Permission.objects.filter(content_type__in=content_types)
    log.debug("Add %i permissions from app '%s'" % (permissions.count(), app_label))
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

    if settings.DEBUG:
        # 'validate' permission string
        # get_permission() will raise helpfull errors if format is wrong
        # or if the permission doesn't exists
        get_permission_by_string(permission)

    if raise_exception:
        log.error(
            'User "%s" has not permission "%s" -> raise PermissionDenied!',
            user, permission
        )
        raise PermissionDenied
    else:
        log.debug('User "%s" has not permission "%s"', user, permission)
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


class ModelPermissionMixin(object):
    """
    Helper for easy model permission checks.
    e.g.:
        class FooModel(ModelPermissionMixin, models.Model):
            ...
            @classmethod
            def has_extra_permission_permission(cls, user, raise_exception=True):
                permission = cls.extra_permission_name(action="extra_permission")
                return check_permission(user, permission, raise_exception)

            class Meta:
                permissions = (
                    ("extra_permission", "Extra permission"),
                )

        def view(request):
            FooModel.has_change_permission(request.user, raise_exception=True)
            FooModel.has_extra_permission_permission(request.user, raise_exception=True)

    See also model used in our tests:
        django_tools_test_project.django_tools_test_app.models.PermissionTestModel
    """
    @classmethod
    def default_permission_name(cls, action):
        """
        Built the permission name for the default add/change/delete permissions.

        Note: Django will add "model name" to these permissions!
        e.g.:
            applabel.add_modelname
            applabel.change_modelname
            applabel.delete_modelname

        https://docs.djangoproject.com/en/1.8/ref/models/options/#default-permissions
        """
        assert action in cls._meta.default_permissions, "'%s' not in Meta.default_permissions !" % action
        permission = "{app}.{action}_{model}".format(
            app=cls._meta.app_label,
            action=action,
            model=cls._meta.model_name,
        )
        return permission

    @classmethod
    def extra_permission_name(cls, action):
        """
        Built permission name for own/extra permissions defined by "ModelClass.Meta.permissions"

        Note: Django will create these permissions without "model name"!
        e.g.:
            applabel.permission_name_modelname
        """
        if settings.DEBUG:
            all_permissions = [p[0] for p in cls._meta.permissions]
            assert action in all_permissions, "'%s' not in Meta.permissions! Existing keys are: %s" % (
                action, ", ".join(all_permissions)
            )
        permission = "{app}.{action}".format(
            app=cls._meta.app_label,
            action=action,
        )
        return permission

    @classmethod
    def has_add_permission(cls, user, raise_exception=True):
        permission = cls.default_permission_name(action="add")
        return check_permission(user, permission, raise_exception)

    @classmethod
    def has_change_permission(cls, user, raise_exception=True):
        permission = cls.default_permission_name(action="change")
        return check_permission(user, permission, raise_exception)

    @classmethod
    def has_delete_permission(cls, user, raise_exception=True):
        permission = cls.default_permission_name(action="delete")
        return check_permission(user, permission, raise_exception)


def get_filtered_permissions(
        exclude_app_labels=None,
        exclude_actions=None,
        exclude_models=None,
        exclude_codenames=None,
        exclude_permissions=None
    ):
    """
    Generate a Permission instance list and exclude parts of it.

    Filters:
        <app_label>.<action>_<modelname>
                    `-----codename-----'

    usage, e.g.:
        permissions = get_filtered_permissions(
            exclude_app_labels=("easy_thumbnails", "filer"),
            exclude_actions=("delete",)
            exclude_models=(LimitToUsergroupsTestModel, PermissionTestModel),
            exclude_codenames=("add_group", "add_user"),
            exclude_permissions=(
                (ContentType, "add_contenttype"),
                (ContentType, "delete_contenttype"),
            )
        )
    """
    qs = Permission.objects.all().order_by("content_type__app_label", "content_type__model", "codename")

    if exclude_codenames is not None:
        qs = qs.exclude(codename__in=exclude_codenames)

    if exclude_actions is not None:
        for action in exclude_actions:
            codename_prefix = "%s_" % action
            qs = qs.exclude(codename__startswith=codename_prefix)

    if exclude_app_labels is not None:
        # SQLite doesn't support .distinct, so we can't do this:
        # app_lables = ContentType.objects.all().values_list("app_label", flat=True).order_by("app_label").distinct("app_label")
        # This isn't perfomance criticle code, isn't it? So just do this:
        app_lables = set(ContentType.objects.all().values_list("app_label", flat=True))

        exclude_content_types = []
        for app_label in exclude_app_labels:
            if app_label not in app_lables:
                raise AssertionError(
                    "app label %r not found! Existing labels: %s" % (
                        app_label, ",".join(app_lables)
                    )
                )
            print("Check %r" % app_label)
            content_types = ContentType.objects.all().filter(app_label = app_label)
            assert content_types.count()>0
            exclude_content_types += content_types

        qs = qs.exclude(content_type__in=exclude_content_types)

    if exclude_models is not None:
        for model in exclude_models:
            content_type = ContentType.objects.get_for_model(model)
            qs = qs.exclude(content_type=content_type)

    if exclude_permissions is not None:
        for model, codename in exclude_permissions:
            content_type = ContentType.objects.get_for_model(model)
            qs = qs.exclude(content_type=content_type, codename=codename)

    return qs


def pprint_filtered_permissions(permissions):
    """
    print a list like this:
        [*] auth.group.add_group
        [*] auth.group.change_group
        [ ] auth.group.delete_group
        [*] auth.permission.add_permission
        [ ] auth.permission.change_permission
        [*] auth.permission.delete_permission
        [*] auth.user.add_user
        [*] auth.user.change_user
        [ ] auth.user.delete_user
        ...
    """
    for permission in permissions:
        assert isinstance(permission, Permission), "List must contain auth.models.Permission instances!"

    qs = Permission.objects.all().order_by("content_type__app_label", "content_type__model", "codename")
    for permission in qs:
        contains = "[*]" if permission in permissions else "[ ]"
        print("%s %s" % (contains, pformat_permission(permission)))
