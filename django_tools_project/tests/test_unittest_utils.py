"""
    :copyleft: 2017-2020 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys

from bx_django_utils.test_utils.html_assertion import HtmlAssertionMixin
from bx_py_utils.path import assert_is_dir, assert_is_file
from django.test import SimpleTestCase, TestCase

from django_tools.template.render import render_string_template
from django_tools.unittest_utils.assertments import (
    assert_endswith,
    assert_equal_dedent,
    assert_in,
    assert_in_dedent,
    assert_path_not_exists,
    assert_pformat_equal,
    assert_startswith,
    dedent,
)
from django_tools.unittest_utils.print_sql import PrintQueries
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.tempdir import TempDir
from django_tools.unittest_utils.template import TEMPLATE_INVALID_PREFIX, set_string_if_invalid
from django_tools.unittest_utils.unittest_base import BaseUnittestCase
from django_tools.unittest_utils.user import TestUserMixin
from django_tools_project.django_tools_test_app.models import PermissionTestModel


class TestBaseUnittestCase(BaseUnittestCase):
    def test_dedent(self):
        """
        Test for BaseUnittestCase._dedent()
        """
        out1 = dedent(
            """
            one line
            line two"""
        )
        assert_pformat_equal(out1, "one line\nline two")

        out2 = dedent(
            """
            one line
            line two
        """
        )
        assert_pformat_equal(out2, "one line\nline two")

        out3 = dedent(
            """
            one line

            line two
        """
        )
        assert_pformat_equal(out3, "one line\n\nline two")

        out4 = dedent(
            """
            one line
                line two

        """
        )
        assert_pformat_equal(out4, "one line\n    line two")

        # removing whitespace and the end
        assert_pformat_equal(dedent("\n  111  \n  222"), "111\n222")

        out5 = dedent(
            """
            one line
                line two
            dritte Zeile
        """
        )
        assert_pformat_equal(out5, "one line\n    line two\ndritte Zeile")

    def test_assertEqual_dedent(self):
        assert_equal_dedent(first="foo bar", second="foo bar")

        with self.assertRaises(AssertionError) as cm:
            assert_equal_dedent(first="foo bar", second="foo X bar")

        error_message = cm.exception.args[0]
        assert error_message == (
            '\x1b[0;34mfirst\x1b[m                                             '
            '\x1b[0;34msecond\x1b[m                                           \n'
            'foo bar                                           foo \x1b[7;1;32mX '
            '\x1b[mbar                                        '
        )

    def test_assert_in_dedent(self):
        assert_in_dedent(member="foo", container="The foo is here!")

        with self.assertRaises(AssertionError) as cm, StdoutStderrBuffer() as buffer:
            assert_in_dedent(member="foo", container="only bar")

        (error_message,) = cm.exception.args
        self.assertEqual(error_message, 'assert_in(): 1 parts not found in content, see output above')

        output = buffer.get_output()
        assert_in(output, parts=('foo', 'only bar'))

    def test_assert_path_not_exists(self):
        assert_path_not_exists("foobar_dir")
        existing_path = os.path.dirname(__file__)
        self.assertRaises(AssertionError, assert_path_not_exists, existing_path)

        assert_path_not_exists("foobar_file.txt")
        self.assertRaises(AssertionError, assert_path_not_exists, __file__)

    def test_assert_startswith(self):
        assert_startswith("foobar", "foo")
        self.assertRaises(AssertionError, assert_startswith, "foobar", "bar")

    def test_assert_endswith(self):
        assert_endswith("foobar", "bar")
        self.assertRaises(AssertionError, assert_endswith, "foobar", "foo")

    def test_get_admin_change_url(self):
        obj = PermissionTestModel.objects.create()
        url = self.get_admin_change_url(obj)
        assert_pformat_equal(url, f"/admin/django_tools_test_app/permissiontestmodel/{obj.pk:d}/change/")

    def test_get_admin_add_url(self):
        url = self.get_admin_add_url(obj=PermissionTestModel)
        assert_pformat_equal(url, "/admin/django_tools_test_app/permissiontestmodel/add/")


class TestTempDir(BaseUnittestCase):
    def testTempDir(self):
        """test TempDir()"""
        with TempDir(prefix="foo_") as tempfolder:
            assert_is_dir(tempfolder)
            self.assertIn(os.sep + "foo_", tempfolder)

            test_filepath = os.path.join(tempfolder, "bar")
            open(test_filepath, "w").close()
            assert_is_file(test_filepath)

        # cleaned?
        assert_path_not_exists(tempfolder)
        assert_path_not_exists(test_filepath)


class TestStdoutStderrBuffer(BaseUnittestCase):
    def test_text_type(self):
        with StdoutStderrBuffer() as buffer:
            print("print text_type")
            sys.stdout.write("stdout.write text_type\n")
            sys.stderr.write("stderr.write text_type")
        assert_equal_dedent(
            buffer.get_output(),
            """
            print text_type
            stdout.write text_type
            stderr.write text_type
        """,
        )


class TestBaseTestCase(TestUserMixin, HtmlAssertionMixin, TestCase):
    def test_print_sql(self):
        with StdoutStderrBuffer() as buffer:
            with PrintQueries("Create object"):
                self.UserModel.objects.all().count()

        output = buffer.get_output()
        # print(output)

        self.assertIn("*** Create object ***", output)
        # FIXME: Will fail if not SQLite/MySQL is used?!?
        self.assertIn("1 - SELECT COUNT(", output)
        self.assertIn('FROM "auth_user"', output)

    def test_create_users(self):
        self.UserModel.objects.all().delete()

        self.create_testusers()

        usernames = self.UserModel.objects.all().values_list("username", flat=True)
        usernames = sorted(usernames)
        assert_pformat_equal(usernames, ["normal_test_user", "staff_test_user", "superuser"])

        # Are all users active?
        assert_pformat_equal(self.UserModel.objects.filter(is_active=True).count(), 3)


@set_string_if_invalid()
class TestSetStringIfInvalidDecorator(SimpleTestCase):
    def assert_activation(self):
        from django.conf import settings

        string_if_invalid = settings.TEMPLATES[0]["OPTIONS"]["string_if_invalid"]
        self.assertIn(TEMPLATE_INVALID_PREFIX, string_if_invalid)

    def test_valid_tag(self):
        self.assert_activation()
        content = render_string_template("pre{{ tag }}post", {"tag": "FooBar!"})
        assert_pformat_equal(content, "preFooBar!post")
        self.assertNotIn(TEMPLATE_INVALID_PREFIX, content)

    def test_invalid_tag(self):
        self.assert_activation()
        content = render_string_template("pre{{ tag }}post", {})
        assert_pformat_equal(content, "pre***invalid:tag***post")
        self.assertIn(TEMPLATE_INVALID_PREFIX, content)
