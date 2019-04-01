"""
    test django_tools.template.loader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2017-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.template import TemplateDoesNotExist

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.unittest_utils.unittest_base import BaseTestCase


class DebugCacheLoaderTest(BaseTestCase):
    def test(self):
        response = self.client.get("/admin/login/")

        self.assertResponse(
            response,
            must_contain=(
                "<!-- START 'admin/login.html' -->",
                "<!-- START 'admin/base_site.html' -->",
                "<!-- START 'admin/base.html' -->",
                "<!-- END 'admin/base.html' -->",
                "<!-- END 'admin/base_site.html' -->",
                "<!-- END 'admin/login.html' -->",
            ),
            must_not_contain=("Error", "Traceback"),
            status_code=200,
            template_name="admin/login.html",
            html=False,
            browser_traceback=True,
        )

    def test_template_does_not_exists(self):
        with self.assertRaises(TemplateDoesNotExist) as cm:
            self.client.get("/raise_template_not_exists/")

        output = "\n".join(cm.exception.args)
        assert_pformat_equal("/template/does/not/exists.html", output)
