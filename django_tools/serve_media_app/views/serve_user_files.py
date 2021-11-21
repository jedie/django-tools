import logging

import django.dispatch
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.views.generic.base import View
from django.views.static import serve

from django_tools.serve_media_app.models import UserMediaTokenModel


logger = logging.getLogger(__name__)

serve_file_request = django.dispatch.Signal()


class UserMediaView(View):
    """
    Serve MEDIA_URL files, but check the current user:
    """

    def check_access_permission(self, request, user_token):
        if request.user.id is None:
            logger.error('Anonymous try to access user media files')
            raise PermissionDenied

        user = request.user

        token = UserMediaTokenModel.objects.get_user_token(user=user)
        if token != user_token:
            # A user tries to access a file from a other user?
            logger.error('Wrong user (%s) token: %r is not %r', user, token, user_token)
            raise PermissionDenied

    def get(self, request, user_token, path):
        media_path = f'{user_token}/{path}'
        logger.debug('Serve: %r', media_path)

        if not request.user.is_superuser:
            self.check_access_permission(request, user_token)

        serve_file_request.send(
            sender=self.__class__,
            user=request.user,
            path=path,
            media_path=media_path
        )

        # Send the file to the user:
        return serve(
            request,
            path=media_path,
            document_root=settings.MEDIA_ROOT,
            show_indexes=False
        )
