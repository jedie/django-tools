#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Show responses in webbrowser
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Helper functions for displaying test responses in webbrowser.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2008-06-13 22:35:31 +0200 (Fr, 13 Jun 2008) $
    $Rev: 1644 $
    $Author: JensDiemer $

    :copyleft: 2009 by the django-dbpreferences team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os, webbrowser, traceback, tempfile
from pprint import pformat

from xml.sax.saxutils import escape

# Bug with Firefox under Ubuntu.
# http://www.python-forum.de/topic-11568.html
#webbrowser._tryorder.insert(0, 'epiphany') # Use Epiphany, if installed.

# Variable to save if the browser is opend in the past.
ONE_DEBUG_DISPLAYED = False

RESPONSE_INFO_ATTR = (
        "content", "context", "cookies", "request", "status_code",
    )


def debug_response(response, one_browser_traceback=True, msg="", \
                                                            display_tb=True):
    """
    Display the response content with a error reaceback in a webbrowser.
    TODO: We should delete the temp files after viewing!
    """
    if one_browser_traceback:
        # Only one traceback should be opend in the browser.
        global ONE_DEBUG_DISPLAYED
        if ONE_DEBUG_DISPLAYED:
            # One browser instance started in the past, skip this error
            return
        else:
            # Save for the next traceback
            ONE_DEBUG_DISPLAYED = True

    content = response.content
    url = response.request["PATH_INFO"]

    stack = traceback.format_stack(limit=3)[:-1]
    stack.append(escape(msg))
    if display_tb:
        print
        print "debug_response:"
        print "-"*80
        print "\n".join(stack)
        print "-"*80

    stack_info = "".join(stack)

    response_info = "<dl>\n"
    for attr in RESPONSE_INFO_ATTR:
        # FIXME: There must be exist a easier way to display the info
        response_info += "\t<dt>%s</dt>\n" % attr
        value = getattr(response, attr, "---")
        value = pformat(value)
        value = escape(value)
        response_info += "\t<dd><pre>%s</pre></dd>\n" % value
    response_info += "</dl>\n"

    if "</body>" in content:
        info = (
            "\n<br /><hr />\n"
            "<h3>Unittest info</h3>\n"
            "<dl>\n"
            "<dt>url:</dt><dd>%s</dd>\n"
            "<dt>traceback:</dt><dd><pre>%s</pre></dd>\n"
            "<dt>response info:</dt>%s\n"
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
    os.write(fd, content)
    os.close(fd)
    url = "file://%s" % file_path
    print "\nDEBUG html page in Browser! (url: %s)" % url
    try:
        webbrowser.open(url)
    except:
        pass
    #time.sleep(0.5)
    #os.remove(file_path)

