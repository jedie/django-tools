"""
    :copyleft: 2017-2020 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
from email.mime.image import MIMEImage

import django
from django.core import mail
from django.test import Client, SimpleTestCase

# https://github.com/jedie/django-tools
from django_tools.mail.send_mail import SendMail
from django_tools.template.render import render_string_template
from django_tools.unittest_utils.assertments import (
    assert_equal_dedent,
    assert_pformat_equal,
    dedent,
)
from django_tools.unittest_utils.email import print_mailbox
from django_tools.unittest_utils.print_sql import PrintQueries
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.tempdir import TempDir
from django_tools.unittest_utils.template import TEMPLATE_INVALID_PREFIX, set_string_if_invalid
from django_tools.unittest_utils.unittest_base import BaseTestCase, BaseUnittestCase
from django_tools.unittest_utils.user import TestUserMixin
from django_tools_test_project.django_tools_test_app.models import PermissionTestModel


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

    def test_assertIn_dedent(self):
        self.assertIn_dedent(member="foo", container="The foo is here!")

        with self.assertRaises(AssertionError) as cm:
            self.assertIn_dedent(member="foo", container="only bar")

        print(repr(cm.exception.args))
        assert cm.exception.args == ("'foo' not found in 'only bar'",)

    # TODO: remove assertments tests in the future!

    def test_assert_is_dir(self):
        existing_path = os.path.dirname(__file__)
        self.assert_is_dir(existing_path)
        self.assertRaises(AssertionError, self.assert_is_dir, "foobar_dir")

    def test_assert_not_is_dir(self):
        self.assert_not_is_dir("foobar_dir")
        existing_path = os.path.dirname(__file__)
        self.assertRaises(AssertionError, self.assert_not_is_dir, existing_path)

    def test_assert_is_file(self):
        self.assert_is_file(__file__)
        self.assertRaises(AssertionError, self.assert_is_file, "foobar_file.txt")

    def test_assert_not_is_File(self):
        self.assert_not_is_File("foobar_file.txt")
        self.assertRaises(AssertionError, self.assert_not_is_File, __file__)

    def test_assert_startswith(self):
        self.assert_startswith("foobar", "foo")
        self.assertRaises(AssertionError, self.assert_startswith, "foobar", "bar")

    def test_assert_endswith(self):
        self.assert_endswith("foobar", "bar")
        self.assertRaises(AssertionError, self.assert_endswith, "foobar", "foo")

    def test_get_admin_change_url(self):
        obj = PermissionTestModel.objects.create()
        url = self.get_admin_change_url(obj)
        if django.VERSION < (1, 11):
            assert_pformat_equal(
                url, f"/admin/django_tools_test_app/permissiontestmodel/{obj.pk:d}/"
            )
        else:
            assert_pformat_equal(
                url, f"/admin/django_tools_test_app/permissiontestmodel/{obj.pk:d}/change/"
            )

    def test_get_admin_add_url(self):
        url = self.get_admin_add_url(obj=PermissionTestModel)
        assert_pformat_equal(url, "/admin/django_tools_test_app/permissiontestmodel/add/")


class TestTempDir(BaseUnittestCase):
    def testTempDir(self):
        """ test TempDir() """
        with TempDir(prefix="foo_") as tempfolder:
            self.assert_is_dir(tempfolder)
            self.assertIn(os.sep + "foo_", tempfolder)

            test_filepath = os.path.join(tempfolder, "bar")
            open(test_filepath, "w").close()
            self.assert_is_file(test_filepath)

        # cleaned?
        self.assert_not_is_dir(tempfolder)
        self.assert_not_is_File(test_filepath)


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

    def test_binary_type(self):
        # The print function will use repr
        with StdoutStderrBuffer() as buffer:
            print(b"print binary_type")
            sys.stdout.write(b"stdout.write binary_type\n")
            sys.stderr.write(b"stderr.write binary_type")
        assert_equal_dedent(
            buffer.get_output(),
            """
            b'print binary_type'
            stdout.write binary_type
            stderr.write binary_type
            """,
        )


class TestBaseTestCase(TestUserMixin, BaseTestCase):
    def test_print_sql(self):
        with StdoutStderrBuffer() as buffer:
            with PrintQueries("Create object"):
                self.UserModel.objects.all().count()

        output = buffer.get_output()
        # print(output)

        self.assertIn("*** Create object ***", output)
        # FIXME: Will fail if not SQLite/MySQL is used?!?
        if django.VERSION < (1, 9):
            self.assertIn("1 - QUERY = 'SELECT COUNT(", output)
        else:
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


class AssertResponseTest(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.response = Client().get("/admin/login/")

    def test_assert_response_ok(self):
        self.assertResponse(
            self.response,
            must_contain=("Django administration", "Username:", "Password:", 'value="Log in"'),
            must_not_contain=("error", "traceback"),
            status_code=200,
            template_name="admin/login.html",
            html=False,
            browser_traceback=True,
        )

    def test_must_contain(self):
        self.assertResponse(self.response, must_contain=("Django administration",))
        self.assertRaises(
            AssertionError,
            self.assertResponse,
            self.response,
            must_contain=("Django X administration",),
            browser_traceback=False,
        )

    def test_must_not_contain(self):
        self.assertRaises(
            AssertionError,
            self.assertResponse,
            self.response,
            must_not_contain=("Django administration",),
            browser_traceback=False,
        )

    def test_wrong_template(self):
        self.assertResponse(self.response, template_name="admin/login.html")
        self.assertRaises(
            AssertionError,
            self.assertResponse,
            self.response,
            template_name="admin/loginXXX.html",
            browser_traceback=False,
        )

    def test_wrong_status_code(self):
        self.assertResponse(self.response, status_code=200)
        self.assertRaises(
            AssertionError,
            self.assertResponse,
            self.response,
            status_code=404,
            browser_traceback=False,
        )

    def test_get_messages_normal_response(self):
        response = self.client.get("/create_message_normal_response/normal-response-message/")

        assert_pformat_equal(self.get_messages(response), ["normal-response-message"])

        self.assertMessages(response, ["normal-response-message"])

        self.assertResponse(
            response,
            must_contain=("django_tools_test_app.views.create_message_normal_response",),
            must_not_contain=("error", "traceback"),
            status_code=200,
            messages=["normal-response-message"],
            html=False,
            browser_traceback=True,
        )

    def test_get_messages_without_context(self):
        response = self.client.get("/create_message_redirect_response/redirect-response-message/")

        assert_pformat_equal(self.get_messages(response), ["redirect-response-message"])

        self.assertMessages(response, ["redirect-response-message"])

        self.assertResponse(response, status_code=302, messages=["redirect-response-message"])

    def test_wrong_messages(self):
        response = self.client.get("/create_message_normal_response/this-is-it/")
        self.assertMessages(response, ["this-is-it"])

        with self.assertRaises(AssertionError) as cm:
            self.assertResponse(response, messages=["this-is-not-it"], browser_traceback=False)

        self.assert_exception_startswith(cm, "Lists differ: ['this-is-it'] != ['this-is-not-it']")

    def test_print_mailbox_no_attachments(self):
        assert_pformat_equal(len(mail.outbox), 0)

        ok = SendMail(
            template_base="mail_test.{ext}",
            mail_context={"foo": "first", "bar": "second"},
            subject="test test_print_mailbox()",
            recipient_list="foo@bar.tld",
        ).send()

        assert_pformat_equal(ok, True)

        assert_pformat_equal(len(mail.outbox), 1)

        with StdoutStderrBuffer() as buff:
            print_mailbox(mail.outbox)
        output = buff.get_output()
        print(output)

        self.assertIn("*** Mail No. 1: ***", output)
        self.assertIn("subject: test test_print_mailbox()", output)
        self.assertIn("<!-- START 'mail_test.txt' -->", output)
        self.assertIn("<!-- END 'mail_test.txt' -->", output)
        self.assertIn("from_email: webmaster@localhost", output)
        self.assertIn("to: ['foo@bar.tld']", output)

    def test_print_mailbox_mime_image(self):
        assert_pformat_equal(len(mail.outbox), 0)

        ok = SendMail(
            template_base="mail_test.{ext}",
            mail_context={"foo": "first", "bar": "second"},
            subject="test test_print_mailbox()",
            recipient_list="foo@bar.tld",
            attachments=[MIMEImage(b"GIF89a This is not a gif picture ;)")],
        ).send()

        assert_pformat_equal(ok, True)

        assert_pformat_equal(len(mail.outbox), 1)

        with StdoutStderrBuffer() as buff:
            print_mailbox(mail.outbox)
        output = buff.get_output()
        print(output)

        self.assertIn("*** Mail No. 1: ***", output)
        self.assertIn("subject: test test_print_mailbox()", output)
        self.assertIn("<!-- START 'mail_test.txt' -->", output)
        self.assertIn("<!-- END 'mail_test.txt' -->", output)
        self.assertIn("from_email: webmaster@localhost", output)
        self.assertIn("to: ['foo@bar.tld']", output)
        self.assertIn("attachments:", output)
        self.assertIn("MIMEImage object", output)
        self.assertIn("b'GIF89a", output)
