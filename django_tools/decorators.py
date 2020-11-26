"""
    some decorators
    ~~~~~~~~~~~~~~~

    from PyLucid decorators.

    :copyleft: 2009-2020 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import sys
import traceback
import warnings
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import render
from django.template import RequestContext
from django.utils.translation import gettext_lazy as _


def check_permissions(superuser_only, permissions=()):
    """
    Protect a view and limit it to users witch are log in and has the permissions.
    If the user is not log in -> Redirect him to a log in view with a next_url back to the requested page.

    TODO: Add a log entry, if user has not all permissions.

    Usage:
    --------------------------------------------------------------------------
    @check_permissions(superuser_only=False, permissions=(u'appname.add_modelname', u'appname.change_modelname'))
    def my_view(request):
        ...
    --------------------------------------------------------------------------
    """
    assert isinstance(superuser_only, bool)
    assert isinstance(permissions, (list, tuple))

    def _inner(view_function):
        @wraps(view_function)
        def _check_permissions(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                # FIXME: HttpResponseRedirect to admin login?
                msg = _("Permission denied for anonymous user. Please log in.")
                if settings.DEBUG:  # Usefull??
                    warnings.warn(msg)
                raise PermissionDenied(msg)

            if not user.has_perms(permissions):
                msg = (
                    f"User {user!r} has not all permissions: {permissions!r}"
                    f" (existing permissions: {user.get_all_permissions()!r})"
                )
                if settings.DEBUG:  # Usefull??
                    warnings.warn(msg)
                raise PermissionDenied(msg)
            return view_function(request, *args, **kwargs)

        # Add superuser_only and permissions attributes, so they are accessible
        # Used to build the admin menu
        _check_permissions.superuser_only = superuser_only
        _check_permissions.permissions = permissions

        return _check_permissions

    return _inner


def render_to(template_name=None, debug=False, **response_kwargs):
    """
    Based on the decorators from django-annoying.

    Example:

        @render_to('foo/template.html')
        def PyLucidPluginFoo(request):
            bar = Bar.object.all()
            return {'bar': bar}

    The view can also insert the template name in the context, e.g.:

        @render_to
        def PyLucidPluginFoo(request):
            bar = Bar.object.all()
            return {'bar': bar, 'template_name': 'foo/template.html'}
    """

    def renderer(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            context = function(*args, **kwargs)

            request = None
            for arg in args:
                if isinstance(arg, HttpRequest):
                    request = arg

            if not request:
                raise AttributeError("Can't get request object from function arguments!")

            if not isinstance(context, dict):
                if debug:
                    msg = (
                        f"renter_to info: {function.__name__}"
                        f" (template: {template_name!r}) has not return a dict,"
                        f" has return: {type(context)!r} ({function.__code__!r})"
                    )
                    messages.info(request, msg)
                return context

            template_name2 = context.pop("template_name", template_name)
            assert template_name2 is not None, (
                "Template name must be passed as render_to parameter"
                " or 'template_name' must be inserted into context!"
            )

            response = render(
                template_name2, context, context=RequestContext(request), **response_kwargs
            )

            if debug:
                messages.info(
                    request,
                    f"render debug for {function.__name__!r} (template: {template_name2!r}):"
                )
                messages.info(request, "local view context:", context)
                messages.info(request, "response:", response.content)

            return response

        return wrapper

    return renderer


def display_admin_error(func):
    """
    For temporary display errors in admin functions. e.g.:

        class MyAdmin(admin.ModelAdmin):

            @display_admin_error
            def bsp(obj):
                raise FooBar

            list_display = ('bsp',)
    """

    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            traceback.print_exc(file=sys.stderr)
            if settings.DEBUG:
                return f"{err.__class__.__name__}: {err}"
            else:
                raise

    return wrapped


def warn_class_usage(message, category=DeprecationWarning):
    """
    create warnings on class usage.
    """

    def cls_wrapper(cls):
        class Wrapped(cls):
            def __init__(self, *args, **kwargs):
                warnings.warn(message, category)
                super().__init__(*args, **kwargs)

            def __new__(cls, *args, **kwargs):
                warnings.warn(message, category)
                return object.__new__(cls)

        return Wrapped

    return cls_wrapper


def warn_function_usage(message, category=DeprecationWarning):
    """
    create warnings on function usage.
    """

    def decorator(function):
        @wraps(function)
        def emit_warning(*args, **kwargs):
            warnings.warn(message, category)
            return function(*args, **kwargs)

        return emit_warning

    return decorator
