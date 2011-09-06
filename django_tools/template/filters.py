# coding: utf-8

"""
    some additional template filters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2007-2009 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import datetime

from django_tools.utils.time_utils import datetime2float


if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode


CHMOD_TRANS_DATA = (
    u"---", u"--x", u"-w-", u"-wx", u"r--", u"r-x", u"rw-", u"rwx"
)
def chmod_symbol(octal_value):
    """
    Transform a os.stat().st_octal_value octal value to a symbolic string.
    ignores meta infromation like SUID, SGID or the Sticky-Bit.
    e.g. 40755 -> rwxr-xr-x
    >>> chmod_symbol(644)
    u'rw-r--r--'
    >>> chmod_symbol(40755)
    u'rwxr-xr-x'
    >>> chmod_symbol("777")
    u'rwxrwxrwx'
    """
    octal_value_string = str(octal_value)[-3:] # strip "meta info"
    return u''.join(CHMOD_TRANS_DATA[int(num)] for num in octal_value_string)
chmod_symbol.is_safe = True
chmod_symbol = stringfilter(chmod_symbol)


def get_oct(value):
    """
    Convert an integer number to an octal string.
    """
    try:
        return oct(value)
    except:
        return value
get_oct.is_safe = False


def human_duration(t):
    """
    Converts a time duration into a friendly text representation.
    
    >>> human_duration("type error")
    Traceback (most recent call last):
        ...
    TypeError: human_duration() argument must be timedelta, integer or float)
    
    
    >>> human_duration(datetime.timedelta(microseconds=1000))
    u'1.0 ms'
    >>> human_duration(0.01)
    u'10.0 ms'
    >>> human_duration(0.9)
    u'900.0 ms'
    >>> human_duration(datetime.timedelta(seconds=1))
    u'1.0 sec'
    >>> human_duration(65.5)
    u'1.1 min'
    >>> human_duration((60 * 60)-1)
    u'59.0 min'
    >>> human_duration(60*60)
    u'1.0 hours'
    >>> human_duration(1.05*60*60)
    u'1.1 hours'
    >>> human_duration(datetime.timedelta(hours=24))
    u'1.0 days'
    >>> human_duration(2.54 * 60 * 60 * 24 * 365)
    u'2.5 years'
    """
    if isinstance(t, datetime.timedelta):
        # timedelta.total_seconds() is new in Python 2.7
        t = datetime2float(t)
    elif not isinstance(t, (int, float)):
        raise TypeError("human_duration() argument must be timedelta, integer or float)")

    chunks = (
      (60 * 60 * 24 * 365, _('years')),
      (60 * 60 * 24 * 30, _('months')),
      (60 * 60 * 24 * 7, _('weeks')),
      (60 * 60 * 24, _('days')),
      (60 * 60, _('hours')),
    )

    if t < 1:
        return _("%.1f ms") % round(t * 1000, 1)
    if t < 60:
        return _("%.1f sec") % round(t, 1)
    if t < 60 * 60:
        return _("%.1f min") % round(t / 60, 1)

    for seconds, name in chunks:
        count = t / seconds
        if count >= 1:
            count = round(count, 1)
            break
    return "%(number).1f %(type)s" % {'number': count, 'type': name}
human_duration.is_safe = True


if __name__ == "__main__":
    import doctest
    print doctest.testmod(verbose=False)
