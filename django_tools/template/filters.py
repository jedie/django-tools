"""
    some additional template filters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2007-2016 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import warnings

from bx_django_utils.humanize.time import human_timedelta
from django.template.defaultfilters import stringfilter


CHMOD_TRANS_DATA = (
    "---", "--x", "-w-", "-wx", "r--", "r-x", "rw-", "rwx"
)


def chmod_symbol(octal_value):
    """
    Transform a os.stat().st_octal_value octal value to a symbolic string.
    ignores meta information like SUID, SGID or the Sticky-Bit.
    e.g. 40755 -> rwxr-xr-x
    >>> chmod_symbol(644)
    'rw-r--r--'
    >>> chmod_symbol(40755)
    'rwxr-xr-x'
    >>> chmod_symbol("777")
    'rwxrwxrwx'
    """
    octal_value_string = str(octal_value)[-3:]  # strip "meta info"
    return ''.join(CHMOD_TRANS_DATA[int(num)] for num in octal_value_string)


chmod_symbol.is_safe = True
chmod_symbol = stringfilter(chmod_symbol)


def get_oct(value):
    """
    Convert an integer number to an octal string.

    >>> get_oct(123)
    '0o173'
    >>> get_oct('abc')
    'abc'
    """
    try:
        return oct(value)
    except TypeError:
        return value


get_oct.is_safe = False


def human_duration(t):
    """
    Converts a time duration into a friendly text representation.

    >>> human_duration(0.01)
    '10.0\xa0ms'
    >>> human_timedelta(59 * 60)
    '59.0\xa0minutes'
    >>> human_duration(1.05*60*60)
    '1.1\xa0hours'
    >>> human_duration(2.54 * 60 * 60 * 24 * 365)
    '2.5\xa0years'
    """
    warnings.warn("Use bx_django_utils.humanize.time.human_timedelta!", DeprecationWarning, stacklevel=2)
    return human_timedelta(t)


human_duration.is_safe = True
