# coding: utf-8

"""
    :copyleft: 2016 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.test import SimpleTestCase

from django_tools.template.render import render_string_template


class TestRender(SimpleTestCase):
    def test_render_string_template(self):
        x = render_string_template("Foo {{ bar }}!", {"bar": "BAR"})
        self.assertEqual(x, 'Foo BAR!')
