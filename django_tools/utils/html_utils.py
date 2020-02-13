"""
    :copyleft: 2017-2020 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import bleach
from django.utils.html import strip_tags


def html2text(value):
    """
    Returns the text from HTML by strip all HTML tags.
    Used first bleach.clean() and then django 'strip_tags'
    """
    if value:
        value = value.strip()

    if value:
        # use Django
        value = strip_tags(value)

        value = bleach.clean(value)

    return value
