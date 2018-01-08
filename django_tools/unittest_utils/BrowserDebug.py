#!/usr/bin/env python
# coding: utf-8

"""
    Show responses in webbrowser
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Helper functions for displaying test responses in webbrowser.

    :copyleft: 2009-2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import cgi
import datetime
import logging
import re
import tempfile
import webbrowser
from collections import OrderedDict
from pprint import pformat
from xml.sax.saxutils import escape

from django.contrib import messages
from django.utils.encoding import force_text
from django.utils.html import strip_tags
from django.views.debug import get_safe_settings

# https://github.com/jedie/django-tools
from django_tools.utils.stack_info import get_stack_info

log = logging.getLogger(__name__)


# Variable to save if the browser was opend in the past.
BROWSER_TRACEBACK_OPENED = False

RESPONSE_INFO_ATTR = (
    "request", "cookies", "status_code", "_headers", "context", "content",
)

TEMP_NAME_PREFIX="django_tools_browserdebug_"
TEMP_DATETIME_FORMAT="%Y%m%d-%H%M%S_"


def filter_html(content):
    content = re.sub(r"(.*?<body>)", "", content) # strip head
    content = re.sub(r"(</body>.*?)", "", content) # strip footer

    # remove style/script blocks:
    content = re.sub(
        r"(<style.*?>.*?</style>)", "", content,
        flags=re.IGNORECASE|re.DOTALL
    )
    content = re.sub(
        r"(<script.*?>.*?</script>)", "", content,
        flags=re.IGNORECASE|re.DOTALL
    )

    content = strip_tags(content)

    # Strip empty lines:
    content = "\n".join([
        line.rstrip()
        for line in content.splitlines()
        if line.strip()
    ])

    return content


def debug_response(response, browser_traceback=True, msg="", display_tb=True, dir=None, print_filtered_html=False):
    """
    Display the response content with a error traceback in a webbrowser.
    TODO: We should delete the temp files after viewing!
    """
    global BROWSER_TRACEBACK_OPENED
    if browser_traceback != True or BROWSER_TRACEBACK_OPENED == True:
        return
    # Save for the next traceback
    BROWSER_TRACEBACK_OPENED = True

    content = response.content.decode("utf-8")

    if print_filtered_html:
        print("="*79)
        print(filter_html(content))
        print("="*79)

    url = response.request["PATH_INFO"]

    stack_info = get_stack_info(filepath_filter="django_tools")
    stack_info.append(msg)
    if display_tb:
        print("\ndebug_response:")
        print("-" * 80)
        print("\n".join(stack_info))
        print("-" * 80)

    stack_info = escape("".join(stack_info))

    response_info = "<dl>\n"

    #-------------------------------------------------------------------------

    response_info += "\t<dt><h3>template</h3> (Without duplicate entries)</dt>\n"
    if hasattr(response, "templates") and response.templates:
        try:
            templates = response.templates
        except AttributeError:
            templates = "---"
        else:
            templates = [template.name for template in OrderedDict.fromkeys(templates)]
            templates = pformat(templates)
            if print_filtered_html:
                print("Used template: %s" % response.templates[0].name)
    else:
        templates = "---"
    response_info += "\t<dd><pre>%s</pre></dd>\n" % templates

    #-------------------------------------------------------------------------

    response_info += "\t<dt><h3>messages</h3></dt>\n"
    msg = messages.get_messages(response.request)
    if msg:
        msg = "".join(["%s\n" % x for x in msg])
    else:
        msg = "---"
    response_info += "\t<dd><pre>%s</pre></dd>\n" % msg

    #-------------------------------------------------------------------------

    # FIXME: Is there a easier way to collect POST data?!?

    response_info += "\t<dt><h3>request.POST</h3></dt>\n"
    try:
        pake_payload = response.request["wsgi.input"] # django.test.client.FakePayload instance
        payload = pake_payload._FakePayload__content
        payload.seek(0)

        pdict = {'boundary':b'BoUnDaRyStRiNg'}
        post_data = cgi.parse_multipart(payload, pdict)

        for k,v in post_data.items():
            post_data[k] = [v.decode("UTF-8") for v in v]

        post_data = pformat(post_data)
    except Exception as err:
        log.error("Can't collect POST data: %s", err)
        post_data = "(Error: %s)" % err

    response_info += "\t<dd><pre>%s</pre></dd>\n" % post_data

    #-------------------------------------------------------------------------

    for attr in RESPONSE_INFO_ATTR:
        # FIXME: There must be exist a easier way to display the info
        response_info += "\t<dt><h3>%s</h3></dt>\n" % attr
        value = getattr(response, attr, "---")
        value = pformat(value)

        try:
            value = force_text(value, errors='strict')
        except UnicodeDecodeError:
            log.exception("decode error in attr %r:" % attr)
            value = force_text(value, errors='replace')

        value = escape(value)
        response_info += "\t<dd><pre>%s</pre></dd>\n" % value

    #-------------------------------------------------------------------------

    response_info += "\t<dt><h3>settings</h3></dt>\n"
    response_info += "\t<dd><pre>%s</pre></dd>\n" % pformat(get_safe_settings())

    response_info += "</dl>\n"

    #-------------------------------------------------------------------------

    if "</body>" in content:
        info = (
            "\n<br /><hr />\n"
            "<h2>Unittest info</h2>\n"
            "<dl>\n"
            "<dt><h3>url:</h3></dt><dd>%s</dd>\n"
            "<dt><h3>traceback:</h3></dt><dd><pre>%s</pre></dd>\n"
            "<dt><h2>response info:</h2></dt>%s\n"
            "</dl>\n"
            "</body>"
        ) % (url, stack_info, response_info)
        content = content.replace("</body>", info)
    else:
        # Not a html page?
        content += "\n<pre>\n"
        content += "-" * 79
        content += (
            "\nUnittest info\n"
            "=============\n"
            "url: %s\n"
            "traceback:\n%s\n</pre>"
            "response info:\n%s\n"
        ) % (url, stack_info, response_info)


    prefix = TEMP_NAME_PREFIX
    dt = datetime.datetime.now()
    prefix += dt.strftime(TEMP_DATETIME_FORMAT)
    with tempfile.NamedTemporaryFile(dir=dir, prefix=prefix, suffix=".html", delete=False) as f:
        f.write(content.encode("utf-8"))

        print("\nWrite time file '%s'" % f.name)

        url = "file://%s" % f.name
        print("\nDEBUG html page in Browser! (url: %s)" % url)
        try:
            webbrowser.open(url)
        except Exception as err:
            log.error("Can't open browser: %s", err)

        return f.name
