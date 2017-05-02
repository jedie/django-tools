# coding: utf-8

"""
    mail util
    ~~~~~~~~~

    :copyleft: 2017 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, absolute_import, print_function

import logging

from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import six

from django_tools.mail.celery_tasks import send_mail_celery_task

log = logging.getLogger(__name__)


class SendMail(object):
    fail_silently=False

    def __init__(self, template_base, mail_context, subject, recipient_list, from_email=None):
        """
        Send a mail in txt and html format
        
        :param template_base: e.g.: /foo/bar.{ext} 
        :param mail_context: django template context used to render the mail
        :param subject: email subject
        :param recipient_list: email recipient
        :param from_email: optional
        """
        self.template_base = template_base
        self.mail_context = mail_context
        self.subject = subject

        assert recipient_list, "No recipient given: %r" % recipient_list
        if isinstance(recipient_list, six.string_types):
            self.recipient_list = [recipient_list]
        else:
            self.recipient_list = recipient_list

        if from_email is None:
            self.from_email = settings.DEFAULT_FROM_EMAIL
        else:
            self.from_email = from_email

    def send(self):
        html_message, text_message = self.render_mail()
        msg = self.create_text_and_html_mail(html_message, text_message)
        return self.send_mail(msg)

    def send_mail(self, msg):
        """
        Send created email.
        """
        return msg.send(fail_silently=self.fail_silently)

    def render_mail(self):
        if isinstance(self.template_base, (list, tuple)):
            template_base_list = self.template_base
            html_template = []
            text_template = []
            for template_base in template_base_list:
                html_template.append(template_base.format(ext='html'))
                text_template.append(template_base.format(ext='txt'))
        else:
            html_template = self.template_base.format(ext='html')
            text_template = self.template_base.format(ext='txt')

        html = render_to_string(html_template, self.mail_context)
        text = render_to_string(text_template, self.mail_context)
        return html, text

    def create_text_and_html_mail(self, html_message, text_message):
        msg = EmailMultiAlternatives(self.subject, text_message, self.from_email, self.recipient_list)
        msg.attach_alternative(html_message, 'text/html')
        return msg


class SendMailCelery(SendMail):
    """
    Create text+html mail and send it via Celery Task Job.
    """
    def send_mail(self, msg):

        send_mail_celery_task(msg)
