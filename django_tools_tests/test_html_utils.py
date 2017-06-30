# coding: utf-8

from __future__ import unicode_literals

from django_tools.unittest_utils.unittest_base import BaseUnittestCase
from django_tools.utils.html_utils import html2text


class TestHtmlUtils(BaseUnittestCase):
    def test_none(self):
        self.assertEqual(html2text(None), None)

    def test_empty(self):
        self.assertEqual(html2text(""), "")

    def test_text_only(self):
        self.assertEqual(html2text("foo"), "foo")

    def test_invalid_tags(self):
        self.assertEqual(html2text("<foo>the text</bar>"), "the text")
