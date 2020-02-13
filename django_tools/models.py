"""
    models stuff
    ~~~~~~~~~~~~

    :copyleft: 2011-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now

# https://github.com/jedie/django-tools
from django_tools.middlewares import ThreadLocal


class UpdateTimeBaseModel(models.Model):
    """
    Base model to automatically set:
     * createtime
     * lastupdatetime

    We doesn't used auto_now_add and auto_now here, because they have the odd side effect
    see also:
    https://github.com/jezdez/django-dbtemplates/commit/2f27327bebe7f2e7b33e5cfb0db517f53a1b9701#commitcomment-1396126
    """

    createtime = models.DateTimeField(default=now, editable=False, help_text="Create time")
    lastupdatetime = models.DateTimeField(default=now, editable=False, help_text="Time of the last change.")

    def __str__(self):  # to be overwritten
        return f"model instance ID:{self.pk}"

    def save(self, *args, **kwargs):
        self.lastupdatetime = now()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


class UpdateUserBaseModel(models.Model):
    """
    Base model to automatically set:
     * createby
     * lastupdateby

    Important: "threadlocals middleware" must be used!
    """

    createby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False,
        related_name="%(class)s_createby",
        null=True,
        blank=True,  # <- If the model used outside a real request (e.g. unittest, db shell)
        help_text="User how create this entry.",
        on_delete=models.SET_NULL,
    )
    lastupdateby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False,
        related_name="%(class)s_lastupdateby",
        null=True,
        blank=True,  # <- If the model used outside a real request (e.g. unittest, db shell)
        help_text="User as last edit this entry.",
        on_delete=models.SET_NULL,
    )

    def __str__(self):  # to be overwritten
        return f"model instance ID:{self.pk}"

    def save(self, *args, **kwargs):
        current_user = ThreadLocal.get_current_user()

        if current_user:
            User = get_user_model()
            if isinstance(current_user, User):
                if self.pk is None or kwargs.get("force_insert", False):  # New model entry
                    self.createby = current_user
                self.lastupdateby = current_user

        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


class UpdateInfoBaseModel(UpdateTimeBaseModel, UpdateUserBaseModel):
    """
    Base model to automatically set:
        * createtime
        * lastupdatetime
    and:
        * createby
        * lastupdateby

    Important: "threadlocals middleware" must be used!
    """

    class Meta:
        abstract = True
