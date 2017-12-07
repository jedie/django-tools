# coding: utf-8

"""
    permission_info manage command


    setup:

        INSTALLED_APPS = [
            ...
            "django_tools",
            ...
        ]


    usage:

        $ ./manage.py permission_info
        $ ./manage.py permission_info <username>


    :copyleft: 2017 by the django-tools team, see AUTHORS for more details.
    :created: 2017 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand

# https://github.com/jedie/django-tools
from django_tools.permissions import pformat_permission


class Command(BaseCommand):
    help = (
        "Display effective user permissions"
        " in the same format as user.has_perm() argument:"
        " <appname>.<codename>"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "user", nargs="?", default=None,
            help="Username"
        )

    def list_usernames(self):
        self.stdout.write("\nAll existing users are:\n")
        UserModel = get_user_model()
        qs = UserModel.objects.all()
        user_count = qs.count()
        usernames = qs.values_list("username", flat=True).order_by("username")
        self.stdout.write(", ".join(usernames))
        self.stdout.write("(%i users)" % user_count)

    def username_error(self):
        self.stderr.write("No username given!")
        self.list_usernames()
        self.stdout.write("")

    def handle(self, *args, **options):
        self.stdout.write("")
        self.stdout.write("_"*79)
        self.stdout.write(self.help)
        self.stdout.write("")

        username = options.get("user")

        if not username:
            self.username_error()
            return

        self.stdout.write("All permissions for user '%s':" % username)

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist as err:
            self.stderr.write("Username %r doesn't exists: %s" % (username, err))
            self.list_usernames()
            return

        for attr_name in ("is_active", "is_staff", "is_superuser"):
            info = "yes" if getattr(user, attr_name) else "no"
            self.stdout.write("\t%-13s: %s" % (attr_name, info))

        if user.is_superuser:
            self.stdout.write("Don't list permissions: Superusers has all permissions ;)")
            return

        from django.contrib import auth
        all_permissions = set()

        for backend in auth.get_backends():
            if hasattr(backend, "get_all_permissions"):
                all_permissions.update(backend.get_all_permissions(user))

        seen_permissions = set()

        qs = Permission.objects.all().order_by("content_type__app_label", "content_type__model", "codename")
        for permission in qs.iterator():
            perm_name = pformat_permission(permission)
            seen_permissions.add(perm_name)

            contains = "[*]" if user.has_perm(perm_name) else "[ ]"
            self.stdout.write("%s %s" % (contains, perm_name))

        # We should never miss a permission, but we can still try it out:
        not_seen = all_permissions - seen_permissions
        for perm_name in sorted(not_seen):
            self.stderr.write("missing: %s" % perm_name)
