# coding: utf-8

"""
    media path selection
    ~~~~~~~~~~~~~~~~~~~~
    
    TODO: Made this generic and don't use settings.MEDIA_ROOT direct, let it
    be set as a argument to widget/fields etc.
    
     * model field
     * form field
     * widget

    :copyleft: 2010 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # For doctest only
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

from django import forms
from django.db import models
from django.conf import settings

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
    dirs.sort(cmp=lambda x, y: cmp(x.lower(), y.lower()))

    for dir in dirs:
        sub_path = os.path.join(path, dir)
        for x in directory_walk(sub_path):
            yield x




class MediaPathWidget(forms.Select):
    """
    Select a sub directory in settings.MEDIA_ROOT
    
    >>> MediaPathWidget().choices # doctest: +ELLIPSIS
    [('/template', '/template'), ..., ('/utils', '/utils')]
    """
    def __init__(self, attrs=None):
        super(MediaPathWidget, self).__init__(attrs)

        self._base_path = os.path.abspath(os.path.normpath(settings.MEDIA_ROOT))

        try:
            self.choices = self._get_path_choices()
        except OSError, err:
            self.choices = []
            if settings.DEBUG:
                failsafe_message("Can't read MEDIA_ROOT: %s" % err)

    def _get_path_choices(self):
        media_dirs_choices = []
        cut_pos = len(self._base_path)
        for root in directory_walk(self._base_path):
            rel_dir = root[cut_pos:].strip(os.sep)
            if rel_dir:
                media_dirs_choices.append((rel_dir, rel_dir))
        return media_dirs_choices


class MediaPathModelField(models.TextField):
    """
    
    """
    __metaclass__ = models.SubfieldBase

#    def __init__(self, separator=",", strip_items=True, skip_empty=True, *args, **kwargs):
#        self.separator = separator
#        self.strip_items = strip_items
#        self.skip_empty = skip_empty
#        super(MediaPathModelField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """ Use always own widget and form field. """
        kwargs["widget"] = MediaPathWidget
#        kwargs["form_class"] = SignSeparatedFormField
        return super(MediaPathModelField, self).formfield(**kwargs)


if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
