"""
    :copyleft: 2017-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.test import SimpleTestCase

# https://github.com/jedie/django-tools
from django_tools.mail.send_mail import SendMail
from django_tools.unittest_utils.assertments import assert_equal_dedent, assert_pformat_equal
from django_tools.unittest_utils.email import print_mailbox
from django_tools.unittest_utils.unittest_base import BaseUnittestCase


class TestEMail(BaseUnittestCase, SimpleTestCase):
    def test_no_recipient(self):
        with self.assertRaises(AssertionError):
            SendMail(
                template_base="mail_test.{ext}",
                mail_context={"foo": "first", "bar": "second"},
                subject="Only a test",
                recipient_list=None,
            )
        with self.assertRaises(AssertionError):
            SendMail(
                template_base="mail_test.{ext}",
                mail_context={"foo": "first", "bar": "second"},
                subject="Only a test",
                recipient_list=[],
            )

    def test_SendMail(self):
        assert_pformat_equal(len(mail.outbox), 0)

        ok = SendMail(
            template_base="mail_test.{ext}",
            mail_context={"foo": "first", "bar": "second"},
            subject="Only a test",
            recipient_list="foo@bar.tld",
        ).send()

        assert_pformat_equal(ok, True)

        print_mailbox(mail.outbox)

        assert_pformat_equal(len(mail.outbox), 1)
        email = mail.outbox[0]
        assert_pformat_equal(email.subject, "Only a test")

        assert_equal_dedent(
            email.body,
            """
            <!-- START 'mail_test.txt' -->
            This is is a test mail.
            It used the django template: first, second

            <!-- END 'mail_test.txt' -->
        """,
        )
        assert_pformat_equal(email.from_email, "webmaster@localhost")
        assert_pformat_equal(email.to, ["foo@bar.tld"])

        self.assertIsInstance(email, EmailMultiAlternatives)

        html_email = email.alternatives[0]

        assert_equal_dedent(
            html_email[0].strip(),
            """
            <!-- START 'mail_test.html' -->
            <!DOCTYPE html>
            <html>
                <head></head>
                <body>
                    <p>This is is a test mail.</br>
                    It used the django template: first, second</p>
                </body>
            </html>


            <!-- END 'mail_test.html' -->
            """,
        )
        assert_pformat_equal(html_email[1], "text/html")
