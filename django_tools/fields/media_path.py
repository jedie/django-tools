"""
    media path selection
    ~~~~~~~~~~~~~~~~~~~~

    TODO: Made this generic and don't use settings.MEDIA_ROOT direct, let it
    be set as a argument to widget/fields etc.

     * model field
     * form field
     * widget

     INFO: This exist only for backward-compatibility and will be removed
     in the future. Please use static_path!

    :copyleft: 2010-2020 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import warnings

from django import forms
from django.conf import settings
from django.db import models

from django_tools.utils.messages import failsafe_message


def directory_walk(path):
    """
    Directory tree generator
    similar to os.walk, except:
      - yield only directories
      - sorted list case-insensitive
      - follow links (os.walk can do this since python 2.6)
    """
    dirs = []
    for name in os.listdir(path):
        if os.path.isdir(os.path.join(path, name)):
            dirs.append(name)

    yield path

    # Sort case-insensitive
    dirs.sort(key=str.lower)

    for dir in dirs:
        sub_path = os.path.join(path, dir)
        yield from directory_walk(sub_path)


class MediaPathWidget(forms.Select):
    """
    Select a sub directory in settings.MEDIA_ROOT
    """

    def __init__(self, attrs=None):
        super().__init__(attrs)

        self._base_path = os.path.abspath(os.path.normpath(settings.MEDIA_ROOT))

        try:
            self.choices = self._get_path_choices()
        except OSError as err:
            self.choices = []
            if settings.DEBUG:
                failsafe_message(f"Can't read MEDIA_ROOT: {err}")

        warnings.warn(
            "MediaPathWidget is deprecated and will removed in the future!"
            " Please use StaticPathWidget.",
            PendingDeprecationWarning
        )

    def _get_path_choices(self):
        media_dirs_choices = []
        cut_pos = len(self._base_path)
        for root in directory_walk(self._base_path):
            rel_dir = root[cut_pos:].strip(os.sep)
            if rel_dir:
                media_dirs_choices.append((rel_dir, rel_dir))
        return media_dirs_choices


class MediaPathModelField(models.TextField):

    def formfield(self, **kwargs):
        """ Use always own widget and form field. """

        warnings.warn(
            "MediaPathModelField is deprecated and will removed in the future!"
            " Please use StaticPathModelField.",
            PendingDeprecationWarning
        )

        kwargs["widget"] = MediaPathWidget
#        kwargs["form_class"] = SignSeparatedFormField
        return super().formfield(**kwargs)
