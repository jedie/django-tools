import os
import sys

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login


User = get_user_model()


# Used values if not defined in settings:
DEFAULT_USERNAME = 'local-test-superuser'
DEFAULT_USERPASS = 'This is no secret!'
DEFAULT_USEREMAIL = 'nobody@local.intranet'
ADMIN_URL_PREFIX = '/admin/'


class AlwaysLoggedInAsSuperUserMiddleware:
    """
    Auto login all users as default superuser. ***** Never use this in production !!! *****
    Default user will be created, if not exist.

    Can be disabled by deactivate the default user.

    WARNING: Include this middleware only in your "local" settings!
    """

    def __init__(self, get_response):
        assert 'RUN_MAIN' in os.environ, 'Only allowed running by Django dev. server !'
        self.get_response = get_response

    def __call__(self, request):
        self._auto_login(request)
        response = self.get_response(request)

        return response

    def _print_and_message(self, request, msg, level=messages.WARNING):
        print(f' *** {msg} ***', file=sys.stderr)
        messages.add_message(request, level, msg)

    def _auto_login(self, request):
        if request.user.is_authenticated:
            return

        # Restrict auto login for the admin:
        admin_url_prefix = getattr(settings, 'ADMIN_URL_PREFIX', ADMIN_URL_PREFIX)
        assert admin_url_prefix.startswith('/')
        if not request.path.startswith(admin_url_prefix):
            return

        username = getattr(settings, 'DEFAULT_USERNAME', DEFAULT_USERNAME)
        email = getattr(settings, 'DEFAULT_USEREMAIL', DEFAULT_USEREMAIL)
        password = getattr(settings, 'DEFAULT_USERPASS', DEFAULT_USERPASS)

        user = self._get_or_create_user(request, username, email, password)
        if user:
            self._print_and_message(request, f'Autologin applied. Your logged in as {username!r}')
            user = authenticate(request=request, username=username, password=password)
            login(request, user)

    def _get_or_create_user(self, request, username, email, password):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self._print_and_message(request, f'Create test django user: {username!r}')
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
        else:
            if not user.is_active:
                self._print_and_message(
                    request, 'Default User was deactivated!', level=messages.ERROR
                )
                return None

            user.set_password(password)
            user.save()
        return user
