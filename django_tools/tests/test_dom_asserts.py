# coding: utf-8

"""
    Test DOM asserts
    ~~~~~~~~~~~~~~~~
    
    Test the DOM unitest stuff from
        Gregor Müllegger GSoC work in the Django soc2011/form-rendering branch

    https://github.com/gregmuellegger/django/blob/soc2011%2Fform-rendering/django/test/testcases.py
    https://github.com/gregmuellegger/django/blob/soc2011%2Fform-rendering/django/test/html.py
    
    :copyleft: 2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest


if __name__ == "__main__":
    # run unittest directly
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django_tools.tests.test_settings"


from django_tools.unittest_utils.unittest_base import BaseTestCase


class FakeResponse(object):
    _charset = "utf-8"
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code


FAKE_RESPONSE1 = FakeResponse("""\
<!DOCTYPE HTML>
<html>
<head><title>A html5 page</title></head>
<body>
<form action="." method="post">
    <div style='display:none'><input type='hidden' name='csrfmiddlewaretoken' value='35e51f70b63058513d571a29465951b4' /></div>
    First name: <input type="text" name="first_name" value="Foo" /><br />
    Last name:<input type="text" name="last_name" value="Bar" /><br />
    <input type="submit" value="Submit" />
</form>
</body></html>""")


class DOMassertTest(BaseTestCase):

    def test_assertHTMLEqual1(self):
        self.assertHTMLEqual(
            '<a href="#" id="foo" class="bar">foobar</a>',
            '<a class="bar" id="foo" href="#">foobar</a>',
        )

    def test_assertHTMLEqual2(self):
        self.assertRaises(AssertionError,
            self.assertHTMLEqual,
            '<a href="#" id="foo" class="bar">foobar</a>',
            '<a class="bar" id="foo" href="#">other</a>',
        )

    def test_html_in_JavaScript1(self):
        """ TODO: https://github.com/gregmuellegger/django/issues/1 """
        self.assertHTMLEqual(
            '<script foo="1" bar="2">var js_sha_link="<p>***</p>"</script>',
            '<script bar="2" foo="1">var js_sha_link="<p>***</p>"</script>',
        )

    def test_html_in_JavaScript2(self):
        """ TODO: https://github.com/gregmuellegger/django/issues/1 """
        self.assertHTMLEqual(
            '<span foo="1" bar="2" /><script> <a href="" /> <p> <span></span> </p> </script>',
            '<span bar="2" foo="1" /><script> <a href="" /> <p> <span></span> </p> </script>',
        )

    def test_closed_input_field(self):
        """ TODO: https://github.com/gregmuellegger/django/issues/2 """
        self.assertHTMLEqual(
            '<input value="Foo" type="text" name="first_name"></input>', ""
        )

    def test_assertDOM1(self):
        self.assertDOM(
            response=FAKE_RESPONSE1,
            must_contain=(
                '<input name="last_name" type="text" value="Bar" />',
                '<input value="Foo" type="text" name="first_name" />',
            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING"),
        )

    def test_assertDOM_must_contain(self):
        self.assertRaises(AssertionError,
            self.assertDOM,
            response=FAKE_RESPONSE1,
            must_contain=(
                '<input name="last_name" type="text" value="Bar" id="error" />',
            ),
            use_browser_traceback=False
        )

    def test_assertDOM_must_not_contain(self):
        self.assertRaises(AssertionError,
            self.assertDOM,
            response=FAKE_RESPONSE1,
            must_not_contain=(
                '<input name="last_name" type="text" value="Bar" />',
            ),
            use_browser_traceback=False
        )

    def test_assertContains1(self):
        self.assertContains(response=FAKE_RESPONSE1,
            text='<input name="last_name" type="text" value="Bar" />',
            count=1, html=True
        )

    def test_assertContains2(self):
        self.assertRaises(AssertionError,
            self.assertContains,
            response=FAKE_RESPONSE1,
            text='<input name="last_name" type="WRONG" value="Bar" />',
            count=1, html=True
        )


if __name__ == "__main__":
    # Run this unitest directly
    unittest.main()

