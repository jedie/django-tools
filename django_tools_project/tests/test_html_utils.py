"""
    :copyleft: 2017-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.unittest_utils.unittest_base import BaseUnittestCase
from django_tools.utils.html_utils import html2text


class TestHtmlUtils(BaseUnittestCase):
    def test_none(self):
        assert_pformat_equal(html2text(None), None)

    def test_empty(self):
        assert_pformat_equal(html2text(""), "")

    def test_text_only(self):
        assert_pformat_equal(html2text("foo"), "foo")

    def test_invalid_tags(self):
        assert_pformat_equal(html2text("<foo>the text</bar>"), "the text")
