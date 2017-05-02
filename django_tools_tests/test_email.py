# coding: utf-8

"""
    :copyleft: 2017 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, absolute_import, print_function

from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.test import SimpleTestCase

from django_tools.mail.send_mail import SendMail, SendMailCelery
from django_tools.unittest_utils.unittest_base import BaseUnittestCase
from django_tools.unittest_utils.celery import task_always_eager


class TestEMail(BaseUnittestCase, SimpleTestCase):
    def test_no_recipient(self):
        with self.assertRaises(AssertionError):
            SendMail(
                template_base="mail_test.{ext}",
                mail_context={"foo": "first", "bar": "second"},
                subject="Only a test",
                recipient_list=None
            )
        with self.assertRaises(AssertionError):
            SendMail(
                template_base="mail_test.{ext}",
                mail_context={"foo": "first", "bar": "second"},
                subject="Only a test",
                recipient_list=[]
            )

    def test_SendMail(self):
        self.assertEqual(len(mail.outbox), 0)

        ok = SendMail(
            template_base="mail_test.{ext}",
            mail_context={"foo": "first", "bar": "second"},
            subject="Only a test",
            recipient_list="foo@bar.tld"
        ).send()

        self.assertEqual(ok, True)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Only a test')
        print(email.body)
        self.assertEqual_dedent(email.body, """
            <!-- START 'mail_test.txt' -->
            This is is a test mail.
            It used the django template: first, second
            
            <!-- END 'mail_test.txt' -->
        """)
        self.assertEqual(email.from_email, 'webmaster@localhost')
        self.assertEqual(email.to, ['foo@bar.tld'])

        self.assertIsInstance(email, EmailMultiAlternatives)

        html_email = email.alternatives[0]
        print(html_email[0].strip())
        self.assertEqual_dedent(html_email[0].strip(), """
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
            """
        )
        self.assertEqual(html_email[1], 'text/html')

    @task_always_eager()
    def test_SendMailCelery(self):
        self.assertEqual(len(mail.outbox), 0)

        SendMailCelery(
            template_base="mail_test.{ext}",
            mail_context={"foo": "first", "bar": "second"},
            subject="Only a test",
            recipient_list="foo@bar.tld"
        ).send()

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Only a test')
        print(email.body)
        self.assertEqual_dedent(email.body, """
            <!-- START 'mail_test.txt' -->
            This is is a test mail.
            It used the django template: first, second
            
            <!-- END 'mail_test.txt' -->
        """)
        self.assertEqual(email.from_email, 'webmaster@localhost')
        self.assertEqual(email.to, ['foo@bar.tld'])

        self.assertIsInstance(email, EmailMultiAlternatives)

        html_email = email.alternatives[0]
        print(html_email[0].strip())
        self.assertEqual_dedent(html_email[0].strip(), """
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
            """
        )
        self.assertEqual(html_email[1], 'text/html')
