# coding: utf-8

"""
    :copyleft: 2016 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.test import SimpleTestCase

from django_tools.template.render import render_string_template, \
    render_template_file


class TestRender(SimpleTestCase):
    def test_render_template_file(self):
        context={"foo":"bar"}
        path = "test_template.html"
        x = render_template_file(path, context)
        self.assertEqual(x, "Hello bar !\n")

    def test_render_string_template(self):
        x = render_string_template("Foo {{ bar }}!", {"bar": "BAR"})
        self.assertEqual(x, 'Foo BAR!')
