# coding: utf-8

"""
    models stuff
    ~~~~~~~~~~~~

    :copyleft: 2011-2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function



from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible

try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now

from django_tools.middlewares import ThreadLocal
try:
    # django 1.6
    from django.contrib.auth import get_user_model
    User = get_user_model()
except:
    # django 1.7
    from django.apps import apps
    user_app, user_model = settings.AUTH_USER_MODEL.split('.')
    User = apps.get_app_config(user_app).get_model(user_model)


@python_2_unicode_compatible
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

    def __str__(self): # to be overwritten
        return "model instance ID:%s" % self.pk

    def save(self, *args, **kwargs):
        self.lastupdatetime = now()
        return super(UpdateTimeBaseModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class UpdateUserBaseModel(models.Model):
    """
    Base model to automatically set:
     * createby
     * lastupdateby
     
    Important: "threadlocals middleware" must be used!
    """
    createby = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, related_name="%(class)s_createby",
        null=True, blank=True, # <- If the model used outside a real request (e.g. unittest, db shell)
        help_text="User how create this entry.")
    lastupdateby = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, related_name="%(class)s_lastupdateby",
        null=True, blank=True, # <- If the model used outside a real request (e.g. unittest, db shell)
        help_text="User as last edit this entry.")

    def __str__(self): # to be overwritten
        return "model instance ID:%s" % self.pk

    def save(self, *args, **kwargs):
        current_user = ThreadLocal.get_current_user()

        if current_user:
            User = get_user_model()
            if isinstance(current_user, User):
                if self.pk == None or kwargs.get("force_insert", False): # New model entry
                    self.createby = current_user
                self.lastupdateby = current_user

        return super(UpdateUserBaseModel, self).save(*args, **kwargs)

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

