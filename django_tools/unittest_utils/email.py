"""
    :created: 2018 by Jens Diemer
    :copyleft: 2018-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from email.mime.image import MIMEImage

from django.utils.text import Truncator


def print_mailbox(outbox, max_length=120):
    """
    Usefull for debugging tests, e.g.:

        # ... do something that send mails
        print_mailbox(mail.outbox)
        self.assertEqual(len(mail.outbox), 2)
    """

    def cutted_bytes(data, num=80):
        return Truncator(repr(data)).chars(num=num)

    print("There are %i mails" % len(outbox))
    for no, mail_instance in enumerate(outbox, start=1):
        print("_" * 79)
        print(f" *** Mail No. {no:d}: ***")

        attr_names = [
            attr_name for attr_name in dir(mail_instance) if not attr_name.startswith("_") and attr_name != "body"
        ]
        attr_names.sort()
        attr_names.append("body")

        for attr_name in attr_names:
            attr = getattr(mail_instance, attr_name, "--")

            if callable(attr) or not isinstance(attr, (str, list, tuple, bool)):
                continue

            print("%20s:" % attr_name, end=" ", flush=True)

            if attr_name == "alternatives":
                for data in attr:
                    print(cutted_bytes(data, num=max_length))

            elif attr_name == "attachments":
                print("\n")
                for attachment in attr:
                    if isinstance(attachment, MIMEImage):
                        line = f" * {attachment!r}"
                        data = attachment.get_payload(decode=True)
                    else:
                        filename, data, mine_type = attachment
                        line = f" * {filename} ({mine_type})"

                    print(line, end=" ")
                    print(cutted_bytes(data, num=(max_length - len(line))))
                print()

            elif attr_name == "body":
                print(attr)
                print("-" * max_length)

            else:
                if len(attr) > max_length:
                    attr = cutted_bytes(data, num=max_length)
                print(attr)

        print("=" * 120)
