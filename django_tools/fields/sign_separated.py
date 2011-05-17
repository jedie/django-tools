# coding: utf-8

"""
    sign separated
    ~~~~~~~~~~~~~~
    
     * model field
     * form field
     * widget

    :copyleft: 2010-2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django_tools.tests.test_settings"

from django import forms
from django.db import models


def _split(raw_value, separator, strip_items, skip_empty):
    if not raw_value:
        return ()

    if isinstance(raw_value, (list, tuple)):
        return raw_value

    values = []
    for item in raw_value.split(separator):
        if strip_items:
            item = item.strip()

        if item in values or skip_empty and not item:
            continue

        values.append(item)

    values = tuple(values)
    return values

def _join(value, separator):
    if value is None:
        value = ""
    elif isinstance(value, (list, tuple)):
        value = separator.join(value)
    return value


class SignSeparatedInput(forms.widgets.Input):
    input_type = 'text'

    def __init__(self, separator=",", *args, **kwargs):
        self.separator = separator
        super(SignSeparatedInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        value = _join(value, self.separator)
        return super(SignSeparatedInput, self).render(name, value, attrs)


class SignSeparatedFormField(forms.CharField):
    """
    >>> SignSeparatedFormField().clean(u"one, two")
    (u'one', u'two')
    
    >>> SignSeparatedFormField().to_python(u"one , two, 3,4")
    (u'one', u'two', u'3', u'4')
    >>> SignSeparatedFormField(strip_items=False).clean(u"one , two, 3,4")
    (u'one ', u' two', u' 3', u'4')
    
    >>> SignSeparatedFormField(separator=" ").clean(u"one  two 3")
    (u'one', u'two', u'3')
    >>> SignSeparatedFormField(separator=" ", skip_empty=False).clean(u"one  two 3")
    (u'one', u'', u'two', u'3')
    
    >>> SignSeparatedFormField().clean(None)
    Traceback (most recent call last):
        ...
    ValidationError: [u'This field is required.']
    
    >>> SignSeparatedFormField().clean("")
    Traceback (most recent call last):
        ...
    ValidationError: [u'This field is required.']
    """
    def __init__(self, separator=",", strip_items=True, skip_empty=True, *args, **kwargs):
        self.separator = separator
        self.strip_items = strip_items
        self.skip_empty = skip_empty

        self.widget = SignSeparatedInput(separator)

        super(SignSeparatedFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        values = _split(value, self.separator, self.strip_items, self.skip_empty)
        return values


class SignSeparatedModelField(models.TextField):
    """
    A dict field.
    Stores a python dict into a text field.
    
    >>> SignSeparatedModelField().to_python("foo, bar")
    ('foo', 'bar')

    >>> SignSeparatedModelField().get_db_prep_save(('foo', 'bar'))
    'foo,bar'
    
    >>> f = SignSeparatedModelField().formfield()
    >>> isinstance(f, SignSeparatedFormField)
    True
    >>> f.clean(u"one , two, 3,4")
    (u'one', u'two', u'3', u'4')
    
    kwargs would be pass to the widget:
    >>> f = SignSeparatedModelField(separator="x", strip_items=False, skip_empty=False).formfield()
    >>> f.clean("1x2x x 3")
    ('1', '2', ' ', ' 3')
    
    
    >>> from django.db import models
    >>> from django.forms.models import ModelForm
        
    >>> class TestModel(models.Model):
    ...     test = SignSeparatedModelField(separator=";")
    ...     class Meta:
    ...         app_label = "django_tools"
    
    >>> class TestForm(ModelForm):
    ...     class Meta:
    ...         model = TestModel
    
    >>> f = TestForm({'test': None})
    >>> f.is_valid()
    False
    >>> f = TestForm({'test': ""})
    >>> f.is_valid()
    False
    >>> f = TestForm({'test': "one; two;three"})
    >>> f.is_valid()
    True
    >>> f.cleaned_data
    {'test': ('one', 'two', 'three')}
    >>> from django.core import management
    >>> management.call_command("syncdb", interactive=False, verbosity=0)
    >>> f.save()
    <TestModel: TestModel object>
    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, separator=",", strip_items=True, skip_empty=True, *args, **kwargs):
        self.separator = separator
        self.strip_items = strip_items
        self.skip_empty = skip_empty
        super(SignSeparatedModelField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """
        Converts the input value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        values = _split(value, self.separator, self.strip_items, self.skip_empty)
        return values

    def get_db_prep_save(self, value, **kwargs):
        "Returns field's value prepared for saving into a database."
        value = _join(value, self.separator)
        return value

    def formfield(self, **kwargs):
        """ Use always own widget and form field. """
        kwargs["separator"] = self.separator
        kwargs["strip_items"] = self.strip_items
        kwargs["skip_empty"] = self.skip_empty

        kwargs["widget"] = SignSeparatedInput
        kwargs["form_class"] = SignSeparatedFormField
        return super(SignSeparatedModelField, self).formfield(**kwargs)



if __name__ == "__main__":
    # Run all unittest directly
    import doctest
    print doctest.testmod(
#        verbose=True
        verbose=False,
    )
    print "DocTest end."
