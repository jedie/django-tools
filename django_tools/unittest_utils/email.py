
"""
    :created: 2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

def print_mailbox(outbox):
    """
    Usefull for debugging tests, e.g.:

        # ... do something that send mails
        print_mailbox(mail.outbox)
        self.assertEqual(len(mail.outbox), 2)
    """
    for no, mail_instance in enumerate(outbox, start=1):
        print("_"*79)
        print(" *** Mail No. %i: ***" % no)
        for attr_name in dir(mail_instance):
            if attr_name.startswith("_"):
                continue
            attr = getattr(mail_instance, attr_name, "--")
            if callable(attr):
                continue
            if not isinstance(attr, (str, bytes, list, tuple, bool)) and attr is not None:
                continue
            if attr_name == "body":
                print("-"*79)
                print("%20s:" % attr_name)
                print(attr)
                print("-"*79)
            else:
                print("%20s: %s" % (attr_name, attr))
        print("="*79)
