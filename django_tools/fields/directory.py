"""
    directory selection
    ~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011-2016 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os

from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_tools import validators


class DirectoryWidget(forms.TextInput):
    """
    TODO: Add AJAX Stuff for easy select a existing directory path.
    """
    pass


class DirectoryFormField(forms.CharField):
    def __init__(self, base_path=settings.MEDIA_ROOT, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(
            validators.ExistingDirValidator(base_path=base_path)
        )

    def clean(self, value):
        value = super().clean(value)
        value = os.path.normpath(value)
        return value


class DirectoryModelField(models.CharField):  # , with_metaclass(models.SubfieldBase)):
    """
    >>> settings.DEBUG=False # Don't add path to error messages
    >>> dir = DirectoryModelField()
    >>> dir.run_validators(settings.MEDIA_ROOT)
    >>> dir.run_validators("does/not/exist")
    Traceback (most recent call last):
    ...
    django.core.exceptions.ValidationError: ["Directory doesn't exist!"]

    >>> dir.run_validators("../")
    Traceback (most recent call last):
    ...
    django.core.exceptions.ValidationError: ['Directory is not in base path!']

    >>> dir = DirectoryModelField(base_path="/")
    >>> dir.run_validators("/etc/default/")
    >>> dir.run_validators("var/log")

    >>> dir.run_validators("../bullshit")
    Traceback (most recent call last):
    ...
    django.core.exceptions.ValidationError: ["Directory doesn't exist!"]
    """
    default_validators = []
    description = _("A existing/accessible directory")

    def __init__(self, max_length=256, base_path=settings.MEDIA_ROOT, *args, **kwargs):
        super().__init__(*args, max_length=max_length, **kwargs)
        self.validators.append(
            validators.ExistingDirValidator(base_path=base_path)
        )

    def formfield(self, **kwargs):
        """ Use always own widget and form field. """
        kwargs["widget"] = DirectoryWidget
        kwargs['form_class'] = DirectoryFormField
        return super().formfield(**kwargs)
