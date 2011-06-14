# coding: utf-8

"""
    models stuff
    ~~~~~~~~~~~~

    :copyleft: 2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.db import models
from django.contrib.auth.models import User


from django_tools.middlewares import ThreadLocal




class UpdateInfoBaseModel(models.Model):
    """
    Base model with update info attributes, used by many models.
    The createby and lastupdateby ForeignKey would be automaticly updated. This needs the 
    request object as the first argument in the save method.
    """
    objects = models.Manager()

    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time")
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.")

    createby = models.ForeignKey(User, editable=False, related_name="%(class)s_createby",
        null=True, blank=True, # <- If the model used outsite a real request (e.g. unittest, db shell)
        help_text="User how create this entry.")
    lastupdateby = models.ForeignKey(User, editable=False, related_name="%(class)s_lastupdateby",
        null=True, blank=True, # <- If the model used outsite a real request (e.g. unittest, db shell)
        help_text="User as last edit this entry.")

    def save(self, *args, **kwargs):
        """
        Automatic update createby and lastupdateby attributes with the request object witch must be
        the first argument.
        """
        current_user = ThreadLocal.get_current_user()

        if current_user and isinstance(current_user, User):
            if self.pk == None or kwargs.get("force_insert", False): # New model entry
                self.createby = current_user
            self.lastupdateby = current_user

        return super(UpdateInfoBaseModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True

