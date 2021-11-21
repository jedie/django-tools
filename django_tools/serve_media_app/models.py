import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_tools.serve_media_app.constants import PATH_TOKEN_LENGTH, USER_TOKEN_LENGTH
from django_tools.serve_media_app.exceptions import NoUserToken
from django_tools.serve_media_app.utils import clean_filename, get_random_string


log = logging.getLogger(__name__)


def generate_token():
    return get_random_string(USER_TOKEN_LENGTH)


def generate_media_path(user, filename):
    """
    Generate random MEDIA path for the given user and filename
    """
    user_token = UserMediaTokenModel.objects.get_user_token(user)

    random_string = get_random_string(PATH_TOKEN_LENGTH)
    filename = clean_filename(filename)
    filename = f'{user_token}/{random_string}/{filename}'

    log.info('Upload file path: %r', filename)
    return filename


def user_directory_path(instance, filename):
    """
    FileField/ImageField 'upload_to' handler
    Function for e.g.: models.ImageField(upload_to=user_directory_path,

    Upload to /MEDIA_ROOT/...
    """
    return generate_media_path(user=instance.user, filename=filename)


class UserMediaTokenQuerySet(models.QuerySet):
    def get_from_user(self, user):
        instance = self.filter(user_id=user.pk).first()
        if not instance:
            # Should be created via migrations/signals for all users
            raise NoUserToken(user=user)  # -> SuspiciousOperation -> HttpResponseBadRequest
        return instance

    def get_user_token(self, user):
        instance = self.get_from_user(user=user)
        if instance is not None:
            return instance.token


class UserMediaTokenModel(models.Model):
    """
    Store for every User a random token.
    This token will be added to uploaded MEDIA files for
    identify the user.
    Auto created via post_save signal, see below.
    """
    objects = UserMediaTokenQuerySet.as_manager()

    user = models.ForeignKey(  # "Owner" of this entry
        settings.AUTH_USER_MODEL,
        related_name='token',
        on_delete=models.CASCADE,
        editable=False,
    )
    token = models.CharField(
        max_length=USER_TOKEN_LENGTH,
        default=generate_token,
        unique=True,
    )

    def __repr__(self):
        return f'<UserMediaTokenModel: user:{self.user_id} token:{self.token!r} ({self.pk})>'


@receiver(post_save, sender=get_user_model())
def create_token(sender, created=None, instance=None, **kwargs):
    assert instance is not None
    token_instance, created = UserMediaTokenModel.objects.get_or_create(user_id=instance.pk)
    if created:
        log.info('User media token created for: %s', instance)
    else:
        log.debug('User media token exists for: %s', instance)
