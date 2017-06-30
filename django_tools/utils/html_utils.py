# coding:utf-8

"""
    :copyleft: 2017 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, absolute_import, print_function

from django.utils.html import strip_tags
from lxml.html.clean import Cleaner


def html2text(value):
    """
    Returns the text from HTML by strip all HTML tags.
    Used first Cleaner() from lxml and then django 'strip_tags'
    """
    if value:
        value = value.strip()

    if value:
        # use lxml cleaner:
        value = Cleaner().clean_html(value)

        # use Django
        value = strip_tags(value)

    return value
