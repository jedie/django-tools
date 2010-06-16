# coding: utf-8

"""
    form widgets
    ~~~~~~~~~~~~

    :copyleft: 2010 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # For doctest only
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings
    global_settings.MEDIA_ROOT = os.path.abspath(".")

from django.conf import settings
from django import forms


class SelectMediaPath(forms.Select):
    """
    Select a sub directory in settings.MEDIA_ROOT
    
    >>> SelectMediaPath().choices # doctest: +ELLIPSIS
    [('/template', '/template'), ..., ('/utils', '/utils')]
    """
    def __init__(self, attrs=None):
        super(SelectMediaPath, self).__init__(attrs)
        self.choices = self._get_path_choices()

    def _get_path_choices(self):
        media_dirs_choices = []
        cut_pos = len(settings.MEDIA_ROOT)
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            rel_dir = root[cut_pos:]
            if rel_dir:
                media_dirs_choices.append((rel_dir, rel_dir))
        return media_dirs_choices


if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
