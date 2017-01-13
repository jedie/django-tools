# coding: utf-8

"""
    Test django_tools.utils.url
"""

from __future__ import unicode_literals

from django.test import SimpleTestCase
from django_tools.utils.url import GetDict


class TestGetDict(SimpleTestCase):
    def test_django_example(self):
        q = GetDict()
        q['next'] = '/a&b/'
        self.assertEqual(q.urlencode(), 'next=%2Fa%26b%2F')
        self.assertEqual(q.urlencode(safe='/'), 'next=/a%26b/')

    def test_empty(self):
        q = GetDict()
        q['this_is_empty'] = None
        self.assertEqual(q.urlencode(), 'this_is_empty')
        q['another_empty'] = None
        self.assertEqual(q.urlencode(), 'another_empty&this_is_empty')

    def test_multi(self):
        q = GetDict(str('vote=yes&vote=no'))
        self.assertEqual(q.urlencode(), 'vote=no&vote=yes')
        q['empty'] = None
        self.assertEqual(q.urlencode(), 'empty&vote=no&vote=yes')

    def test_enhanced_example(self):
        q = GetDict()
        q['next'] = '/a&b/'
        q['foo'] = 'bar'
        q['number'] = 123
        q['empty'] = None
        self.assertEqual(q.urlencode(), 'empty&foo=bar&next=%2Fa%26b%2F&number=123')
        self.assertEqual(q.urlencode(safe='/'), 'empty&foo=bar&next=/a%26b/&number=123')
