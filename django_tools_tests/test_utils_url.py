"""
    Test django_tools.utils.url

    :copyleft: 2017-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from django.test import SimpleTestCase

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.utils.url import GetDict


class TestGetDict(SimpleTestCase):
    def test_django_example(self):
        q = GetDict()
        q["next"] = "/a&b/"
        assert_pformat_equal(q.urlencode(), "next=%2Fa%26b%2F")
        assert_pformat_equal(q.urlencode(safe="/"), "next=/a%26b/")

    def test_empty(self):
        q = GetDict()
        q["this_is_empty"] = None
        assert_pformat_equal(q.urlencode(), "this_is_empty")
        q["another_empty"] = None
        assert_pformat_equal(q.urlencode(), "another_empty&this_is_empty")

    def test_multi(self):
        q = GetDict("vote=yes&vote=no")
        assert_pformat_equal(q.urlencode(), "vote=no&vote=yes")
        q["empty"] = None
        assert_pformat_equal(q.urlencode(), "empty&vote=no&vote=yes")

    def test_enhanced_example(self):
        q = GetDict()
        q["next"] = "/a&b/"
        q["foo"] = "bar"
        q["number"] = 123
        q["empty"] = None
        assert_pformat_equal(q.urlencode(), "empty&foo=bar&next=%2Fa%26b%2F&number=123")
        assert_pformat_equal(q.urlencode(safe="/"), "empty&foo=bar&next=/a%26b/&number=123")
