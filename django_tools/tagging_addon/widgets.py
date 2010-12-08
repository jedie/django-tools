#coding:utf-8

"""
    Addon for django-tagging
    
    http://code.google.com/p/django-tagging/
    
    Some code parts from http://code.google.com/p/django-tagging-autocomplete/    
    
    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.forms.widgets import TextInput
from tagging.models import Tag
from django.template.loader import render_to_string


class jQueryTagFieldWidget(TextInput):
    """
    A widget for a django-tagging field. Display existing tags and make them
    clickable with jQuery.
    
    Needs as first initial argument the model class for Tag.objects.cloud_for_model()
    
    To change the "Tag cloud_for_model queryset filters" do this, e.g.:
    ---------------------------------------------------------------------------
    class FooBarForm(forms.ModelForm):
    
        def __init__(self, *args, **kwargs):
            super(FooBarForm, self).__init__(*args, **kwargs)
            
            site = self.initial.get("site", None) or self.data.get("site", None) or settings.SITE_ID
            
            # change the tag queryset filter:
            self.fields["tags"].widget.tag_queryset_filters = {
                "site": site
            }
            
            self._setup_tag_filter()
    
        class Meta:
            model = FooBarModel
    
    --------------------------------------------------------------------------- 
    """
    def __init__(self, tag_model, *args, **kwargs):
        self.tag_model = tag_model
        self.tag_queryset_filters = kwargs.pop("tag_queryset_filters", {})
        super(jQueryTagFieldWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        html = super(jQueryTagFieldWidget, self).render(name, value, attrs)
        tag_cloud = Tag.objects.cloud_for_model(self.tag_model, steps=2, filters=self.tag_queryset_filters)
        context = {
            "html": html,
            "tag_cloud": tag_cloud,
            "field_id": attrs['id'],
        }
        return render_to_string("tagging_addon/jQueryTagField.html", context)
