"""
    created 25.09.2019 by Jens Diemer
    :copyleft: 2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import time

from django.core import mail
from django.test import override_settings

# https://github.com/jedie/django-tools
from django_tools.log_utils.throttle_admin_email_handler import ThrottledAdminEmailHandler
from django_tools.unittest_utils.email import print_mailbox


@override_settings(ADMINS=(("Mr. Test", "foo.bar@example.tld"),))
def test_throttle_admin_email_handler():

    handler = ThrottledAdminEmailHandler(min_delay_sec=0.1)

    for char in ("A", "B"):
        for no in range(3):
            handler.send_mail(subject=f"subject {char} {no:d}", message=f"message {char} {no:d}")

        time.sleep(0.11)
        handler.send_mail(subject=f"subject {char} last", message=f"message {char} last")
        time.sleep(0.11)

    print_mailbox(mail.outbox)
    assert len(mail.outbox) == 4

    ##########################################################################
    # 1. "normal" mail:

    email = mail.outbox[0]
    assert "subject A 0" in email.subject
    assert "message A 0" in email.body
    assert "skipped mails" not in email.body

    ##########################################################################
    # 2. mail with skipped mails:

    email = mail.outbox[1]
    assert "subject A last" in email.subject

    assert "2 skipped mails" in email.body
    assert "* subject A 1" in email.body
    assert "* subject A 2" in email.body

    assert "message A last" in email.body

    ##########################################################################
    # 3. "normal" mail:

    email = mail.outbox[2]
    assert "subject B 0" in email.subject
    assert "message B 0" in email.body
    assert "skipped mails" not in email.body

    ##########################################################################
    # 4. mail with skipped mails:

    email = mail.outbox[3]
    assert "subject B last" in email.subject

    assert "2 skipped mails" in email.body
    assert "* subject B 1" in email.body
    assert "* subject B 2" in email.body

    assert "message B last" in email.body
