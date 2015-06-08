# coding: utf-8

"""   
    template render
    ~~~~~~~~~~~~~~
    
    Some tools around template rendering
    
    :copyleft: 2009-2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

from django.template import Context, Template

def render_string_template(template, context):
    """
    render the given template string with the context and return it as a string
    
    >>> x = render_string_template("Foo {{ bar }}!", {"bar": "BAR"})
    >>> x == 'Foo BAR!'
    True
    """
    t = Template(template)
    c = Context(context)
    return t.render(c)


