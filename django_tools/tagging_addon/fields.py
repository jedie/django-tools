# coding:utf-8

"""
    Addon for django-tagging
    
    http://code.google.com/p/django-tagging/
    
    Some code parts from http://code.google.com/p/django-tagging-autocomplete/    
    
    :copyleft: 2010-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from tagging.fields import TagField
from django_tools.tagging_addon.widgets import jQueryTagFieldWidget


class jQueryTagModelField(TagField):
    """
    A model field for a django-tagging field.
    Use a own widget to display existing tags and make them clickable with jQuery. 
    """
    def formfield(self, **kwargs):
        # Use our own widget and give him access to the model class
        kwargs['widget'] = jQueryTagFieldWidget(self.model)
        return super(jQueryTagModelField, self).formfield(**kwargs)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^django_tools\.tagging_addon\.fields\.jQueryTagModelField"])
except ImportError:
    pass
