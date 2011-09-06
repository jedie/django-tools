# coding: utf-8

"""
    utils around time/date/datetime
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import datetime


def datetime2float(t):
    """  
    >>> datetime2float(datetime.timedelta(seconds=1))
    1.0
    
    >>> f = datetime2float(datetime.timedelta(weeks=2, seconds=20.1, microseconds=100))
    >>> f
    1209620.1001
    >>> f == 20.1 + 0.0001 + 2 * 7 * 24 * 60 * 60 
    True
    
    >>> datetime2float("type error")
    Traceback (most recent call last):
        ...
    TypeError: datetime2float() argument must be a timedelta instance.
    """
    if not isinstance(t, datetime.timedelta):
        raise TypeError("datetime2float() argument must be a timedelta instance.")

    # timedelta.total_seconds() is new in Python 2.7
    return (float(t.microseconds) + (t.seconds + t.days * 24 * 3600) * 1E6) / 1E6


if __name__ == "__main__":
    import doctest
    print doctest.testmod(verbose=False)
