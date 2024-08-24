"""
    test django_tools.template.loader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2017-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from bx_django_utils.test_utils.html_assertion import HtmlAssertionMixin
from django.template import TemplateDoesNotExist
from django.test import TestCase

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_pformat_equal


class DebugCacheLoaderTest(HtmlAssertionMixin, TestCase):
    def test(self):
        response = self.client.get("/admin/login/")
        self.assert_html_parts(
            response,
            parts=(
                "<!-- START 'admin/login.html' -->",
                "<!-- START 'admin/base_site.html' -->",
                "<!-- START 'admin/base.html' -->",
                "<!-- END 'admin/base.html' -->",
                "<!-- END 'admin/base_site.html' -->",
                "<!-- END 'admin/login.html' -->",
            ),
        )
        self.assertTemplateUsed(response, "admin/login.html")

    def test_template_does_not_exists(self):
        with self.assertRaises(TemplateDoesNotExist) as cm:
            self.client.get("/raise_template_not_exists/")

        output = "\n".join(cm.exception.args)
        assert_pformat_equal("/template/does/not/exists.html", output)
