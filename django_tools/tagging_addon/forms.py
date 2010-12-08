#coding:utf-8

"""
    Addon for django-tagging
    
    http://code.google.com/p/django-tagging/
    
    Some code parts from http://code.google.com/p/django-tagging-autocomplete/    
    
    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from tagging.forms import TagField
from django_tools.tagging_addon.widgets import jQueryTagFieldWidget

class jQueryTagFormField(TagField):
    """
    A form field for a django-tagging field.
    Use a own widget to display existing tags and make them clickable with jQuery.
    
    Needs as first initial argument the model class for the own widget.
    """
    def __init__(self, tag_model, *args, **kwargs):
        self.tag_model = tag_model
        kwargs["widget"] = jQueryTagFieldWidget(tag_model)
        super(jQueryTagFormField, self).__init__(*args, **kwargs)
