"""
    ThrottledAdminEmailHandler
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    created 25.09.2019 by Jens Diemer
    :copyleft: 2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging
import time

from django.core import mail
from django.utils.log import AdminEmailHandler


log = logging.getLogger(__name__)


class ThrottledAdminEmailHandler(AdminEmailHandler):
    """
    Throttled email handler.

    Works similar as the origin django.utils.log.AdminEmailHandler
    But mails send in >min_delay_sec< time range will be skiped.
    The mail subject of skipped mails will be added to the next error mails.

    Note: Currently "include_html" is not supported and will be deactivated!

    usage, e.g.:

        LOGGING = {
            # ...
            "handlers": {
                "mail_admins": {
                    "level": "ERROR",
                    "class": "django_tools.log_utils.throttle_admin_email_handler.ThrottledAdminEmailHandler",
                    "formatter": "email",
                    "min_delay_sec": 20, # << -- skip mails in this time range
                },
                # ...
            },
            # ...
        }
    """

    def __init__(self, *args, min_delay_sec=30, **kwargs):
        super().__init__(*args, **kwargs)

        self.include_html = False  # TODO: support html mails, too

        self.min_delay_sec = min_delay_sec
        self.next_mail = None
        self.skipped_subjects = []

    def send_mail(self, subject, message, *args, **kwargs):
        if self.next_mail:
            if self.next_mail > time.time():
                log.debug("Throttle error mail: %r", subject)
                self.skipped_subjects.append(subject)
                return

        if self.skipped_subjects:
            prefix = "\nNote: there are %i skipped mails:\n" % len(self.skipped_subjects)
            prefix += "\n\t* " + "\n\t* ".join(self.skipped_subjects)
            prefix += "\n\n"
            message = prefix + message
            self.skipped_subjects.clear()

        log.debug("Send mail: %r", subject)

        mail.mail_admins(subject, message, *args, connection=self.connection(), **kwargs)

        self.next_mail = time.time() + self.min_delay_sec
