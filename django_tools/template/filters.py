# -*- coding: utf-8 -*-

"""
    some additional template filters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2008-08-15 10:37:58 +0200 (Fr, 15 Aug 2008) $
    $Rev: 1728 $
    $Author: JensDiemer $

    :copyleft: 2007-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode


CHMOD_TRANS_DATA = (
    u"---", u"--x", u"-w-", u"-wx", u"r--", u"r-x", u"rw-", u"rwx",
)
def chmod_symbol(mod):
    """
    Transform a os.stat().st_mode octal value to a symbolic string.
    ignores meta infromation like SUID, SGID or the Sticky-Bit.
    e.g. 40755 -> rwxr-xr-x
    """
    try:
        mod = int(mod) # The django template engine gives always a unicode string
    except ValueError:
        return u""
    mod = mod & 0777 # strip "meta info"
    mod_string = u"%o" % mod

    return u''.join(CHMOD_TRANS_DATA[int(num)] for num in mod_string)
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
    Note: Used in the PyLucid cache middleware, too.
    """
    if t < 1:
        return _("%.1f ms") % (t * 1000)
    elif t > 60:
        return _("%.1f min") % (t / 60.0)
    else:
        return _("%.1f sec") % t
human_duration.is_safe = True
