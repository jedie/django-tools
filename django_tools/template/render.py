# coding: utf-8

"""   
    template render
    ~~~~~~~~~~~~~~
    
    Some tools around template rendering
    
    :copyleft: 2009 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

from django.template import Context, Template

def render_string_template(template, context):
    """
    render the given template string with the context and return it as a string
    
    >>> render_string_template("Foo {{ bar }}!", {"bar": "BAR"})
    u'Foo BAR!'
    """
    t = Template(template)
    c = Context(context)
    return t.render(c)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
    print "DocTest end."