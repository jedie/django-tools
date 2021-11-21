import os
import sys

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


# Used values if not defined in settings:
DEFAULT_USERNAME = 'local-test-superuser'
DEFAULT_USERPASS = 'This is no secret!'
DEFAULT_USEREMAIL = 'nobody@local.intranet'


def _print_and_message(request, msg, level=messages.WARNING):
    print(f' *** {msg} ***', file=sys.stderr)
    messages.add_message(request, level, msg)


class AlwaysLoggedInAsSuperUserMiddleware:
    """
    Auto login all users as default superuser.
    Default user will be created, if not exist.

    Disable it by deactivate the default user.

    WARNING: Include this middleware only in your "local" settings!
    """

    def __init__(self, get_response):
        assert 'RUN_MAIN' in os.environ, 'Only allowed running by Django dev. server !'
        self.get_response = get_response

    def __call__(self, request):
        self._auto_login(request)
        response = self.get_response(request)

        return response

    def _auto_login(self, request):
        if request.user.is_authenticated:
            return

        username = getattr(settings, 'DEFAULT_USERNAME', DEFAULT_USERNAME)
        email = getattr(settings, 'DEFAULT_USEREMAIL', DEFAULT_USEREMAIL)
        password = getattr(settings, 'DEFAULT_USERPASS', DEFAULT_USERPASS)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            _print_and_message(request, f'Create test django user: {username!r}')
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
        else:
            if not user.is_active:
                _print_and_message(request, 'Default User was deactivated!', level=messages.ERROR)
                return

            user.set_password(password)
            user.save()

        _print_and_message(
            request,
            f'Autologin applied. Your logged in as {username!r}'
        )
        user = authenticate(
            request=request,
            username=username,
            password=password
        )
        login(request, user)
