# coding: utf-8

"""
    Send warnings if a template variable does not exist in the content.

    experimental.

    Put this into your settings.py:
    --------------------------------------------------------------------------
    if DEBUG:
        from django_tools.template import warn_invalid_template_vars
        warn_invalid_template_vars.add_warning()
    --------------------------------------------------------------------------
"""

import warnings

from django import template
# from django.utils.encoding import smart_unicode, force_unicode, smart_str

_WARN_ADDED = False

MAX_LEN = 79

class InvalidTemplateKey(Warning):
    pass

def add_warning():
    global _WARN_ADDED
    if _WARN_ADDED:
        return

    class WarnVariableDoesNotExist(template.VariableDoesNotExist):
        def __init__(self, *args, **kwargs):
            super(WarnVariableDoesNotExist, self).__init__(*args, **kwargs)

            warn_msg = str(self) # get the complete message encoded in UTF-8
            if len(warn_msg) > MAX_LEN:
                warn_msg = warn_msg[:MAX_LEN] + "..."
            warnings.warn(warn_msg, category=InvalidTemplateKey)

    template.VariableDoesNotExist = WarnVariableDoesNotExist

    _WARN_ADDED = True
