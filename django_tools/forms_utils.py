# coding: utf-8

"""
    forms utils
    ~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:$

    :copyleft: 2009 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


from django import forms


class LimitManyToManyFields(object):
    """
    Limit ManyToMany fields in forms. Hide the field, if only one item can be selected.
    
    e.g. limit sites choices only to accessible sites:
    --------------------------------------------------------------------------
    class MyModel(models.Model):
        sites = models.ManyToManyField(Site)
        ...
        
    class UserProfile(models.Model):
        sites = models.ManyToManyField(Site)
        ...
        
    class MyForm(LimitManyToManyFields, forms.ModelForm): # <- Order is important !
        class Meta:
            model = MyModel
            
    def my_view(request):
        user_profile = request.user.get_profile()

        m2m_limit = {"sites": user_profile.sites.values_list("id", "name")}
        
        if request.method == "POST":
            form = MyForm(m2m_limit, request.POST)
            if form.is_valid():
                ...
        else:
            # Preselect all existing sites
            form = MyForm(m2m_limit)
        ...
    --------------------------------------------------------------------------
    
    crosspost: http://www.djangosnippets.org/snippets/1692/
    """
    def __init__(self, m2m_limit, *args, **kwargs):
        """
        preselect site select options. If user can only access one site or there exist only one site
        we remove the site field and insert the site info in save() method.
        """
        assert isinstance(m2m_limit, dict), \
            "%s error: first argument must be the m2m limit dict!" % self.__class__.__name__

        super(LimitManyToManyFields, self).__init__(*args, **kwargs)

        for field_name, limits in m2m_limit.items():
            if len(limits) == 1:
                value = int(limits[0][0])
                # Only one item can be selected. Hide the ManyToMany field. To hide the field and
                # for validation, we changed the MultipleChoiceField to a IntegerField.
                self.fields[field_name] = forms.IntegerField(
                    max_value=value, min_value=value, initial=value
                )
#                self.fields[field_name].widget.input_type = 'hidden'
#                self.fields[field_name].widget.is_hidden = True
            else:
                # Limit the ManyToMany field choices
                self.fields[field_name].choices = limits


