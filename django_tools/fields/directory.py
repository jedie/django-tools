# coding: utf-8


"""
    directory selection
    ~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011-2016 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import os

from django import forms
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.six import with_metaclass

from django_tools.utils.messages import failsafe_message
from django_tools import validators


class DirectoryWidget(forms.TextInput):
    """
    TODO: Add AJAX Stuff for easy select a existing directory path.
    """
    pass


class DirectoryFormField(forms.CharField):
    def __init__(self, base_path=settings.MEDIA_ROOT, *args, **kwargs):
        super(DirectoryFormField, self).__init__(*args, **kwargs)
        self.validators.append(
            validators.ExistingDirValidator(base_path=base_path)
        )

    def clean(self, value):
        value = super(DirectoryFormField, self).clean(value)
        value = os.path.normpath(value)
        return value


class DirectoryModelField(models.CharField):#, with_metaclass(models.SubfieldBase)):
    """
    >>> dir = DirectoryModelField()
    >>> dir.run_validators(settings.MEDIA_ROOT)
    >>> try:
    ...     dir.run_validators("does/not/exist")
    ... except Exception as err:
    ...     print(err.__class__.__name__, err)
    ValidationError ["Directory doesn't exist!"]

    >>> try:
    ...     dir.run_validators("../")
    ... except Exception as err:
    ...     print(err.__class__.__name__, err)
    ValidationError ['Directory is not in base path!']

    >>> dir = DirectoryModelField(base_path="/")
    >>> dir.run_validators("/etc/default/")
    >>> dir.run_validators("var/log")

    >>> try:
    ...     dir.run_validators("../bullshit")
    ... except Exception as err:
    ...     print(err.__class__.__name__, err)
    ValidationError ["Directory doesn't exist!"]
    """
    default_validators = []
    description = _("A existing/accessible directory")

    def __init__(self, max_length=256, base_path=settings.MEDIA_ROOT, *args, **kwargs):
        super(DirectoryModelField, self).__init__(*args, max_length=max_length, **kwargs)
        self.validators.append(
            validators.ExistingDirValidator(base_path=base_path)
        )

    def formfield(self, **kwargs):
        """ Use always own widget and form field. """
        kwargs["widget"] = DirectoryWidget
        kwargs['form_class'] = DirectoryFormField
        return super(DirectoryModelField, self).formfield(**kwargs)
