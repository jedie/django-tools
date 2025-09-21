"""
    static path selection
    ~~~~~~~~~~~~~~~~~~~~

    TODO: Made this generic and don't use settings.STATIC_ROOT direct, let it
    be set as a argument to widget/fields etc.

     * model field
     * form field
     * widget

    :copyleft: 2012-2025 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from pathlib import Path

from django import forms
from django.conf import settings
from django.db import models

from django_tools.utils.messages import failsafe_message


class StaticPathWidget(forms.Select):
    """
    Select a sub directory in settings.STATIC_ROOT
    """

    def __init__(self, attrs=None):
        super().__init__(attrs)

        base_path = Path(settings.STATIC_ROOT)
        if not base_path.is_dir():
            self.choices = []
            if settings.DEBUG:
                failsafe_message(f"Can't read STATIC_ROOT: {base_path}")
        else:
            dirs = [str(sub_path.relative_to(base_path)) for sub_path in base_path.rglob('*') if sub_path.is_dir()]
            self.choices = [(d, d) for d in sorted(dirs, key=str.lower)]


class StaticPathModelField(models.TextField):
    """
    Model field for select a sub directory in settings.STATIC_ROOT
    """

    def formfield(self, **kwargs):
        """Use always own widget and form field."""
        kwargs['widget'] = StaticPathWidget
        return super().formfield(**kwargs)
