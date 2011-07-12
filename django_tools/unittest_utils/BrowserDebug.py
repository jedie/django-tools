#!/usr/bin/env python
# coding: utf-8

"""
    Show responses in webbrowser
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Helper functions for displaying test responses in webbrowser.

    :copyleft: 2009-2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pprint import pformat
from xml.sax.saxutils import escape
import os
import tempfile
import webbrowser

from django.contrib import messages
from django.views.debug import get_safe_settings

from django_tools.utils.stack_info import get_stack_info


# Bug with Firefox under Ubuntu.
# http://www.python-forum.de/topic-11568.html
#webbrowser._tryorder.insert(0, 'epiphany') # Use Epiphany, if installed.

# Variable to save if the browser is opend in the past.
BROWSER_TRACEBACK_OPENED = False

RESPONSE_INFO_ATTR = (
    "content", "cookies", "request", "status_code", "_headers", "context",
)





def debug_response(response, browser_traceback=True, msg="", display_tb=True):
    """
    Display the response content with a error reaceback in a webbrowser.
    TODO: We should delete the temp files after viewing!
    """
    global BROWSER_TRACEBACK_OPENED
    if browser_traceback != True or BROWSER_TRACEBACK_OPENED == True:
        return
    # Save for the next traceback
    BROWSER_TRACEBACK_OPENED = True

    content = response.content.decode("utf-8")
    url = response.request["PATH_INFO"]

    stack_info = get_stack_info(filepath_filter="django_tools")
    stack_info.append(msg)
    if display_tb:
        print
        print "debug_response:"
        print "-" * 80
        print "\n".join(stack_info)
        print "-" * 80

    stack_info = escape("".join(stack_info))

    response_info = "<dl>\n"

    response_info += "\t<dt><h3>template</h3></dt>\n"
    if hasattr(response, "templates") and response.templates:
        try:
            templates = pformat([template.name for template in response.templates])
        except AttributeError:
            templates = "---"
    else:
        templates = "---"
    response_info += "\t<dd><pre>%s</pre></dd>\n" % templates

    response_info += "\t<dt><h3>messages</h3></dt>\n"
    msg = messages.get_messages(response.request)
    if msg:
        msg = "".join(["%s\n" % x for x in msg])
    else:
        msg = "---"
    response_info += "\t<dd><pre>%s</pre></dd>\n" % msg

    for attr in RESPONSE_INFO_ATTR:
        # FIXME: There must be exist a easier way to display the info
        response_info += "\t<dt><h3>%s</h3></dt>\n" % attr
        value = getattr(response, attr, "---")
        value = pformat(value)
        value = escape(value)
        response_info += "\t<dd><pre>%s</pre></dd>\n" % value

    response_info += "\t<dt><h3>settings</h3></dt>\n"
    response_info += "\t<dd><pre>%s</pre></dd>\n" % pformat(get_safe_settings())

    response_info += "</dl>\n"


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


    fd, file_path = tempfile.mkstemp(prefix="PyLucid_unittest_", suffix=".html")
    os.write(fd, content.encode("utf-8"))
    os.close(fd)
    url = "file://%s" % file_path
    print "\nDEBUG html page in Browser! (url: %s)" % url
    try:
        webbrowser.open(url)
    except:
        pass
    #time.sleep(0.5)
    #os.remove(file_path)

