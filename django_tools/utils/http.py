# encoding: utf-8

"""
    http utils
    ~~~~~~~~~~
    
    Small helpers around getting a webpage via http GET.
    
    You can easy get a web page encoding in unicode with HttpRequest().
    
    HttpRequest() and HTTPHandler2() make it possible to get the complete
    sended request headers. See also:
    http://stackoverflow.com/questions/603856/get-urllib2-request-headers
    
    more info, see DocStrings below...
    
    :copyleft: 2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import httplib
import urllib2
import cgi
import re


class HTTPConnection2(httplib.HTTPConnection):
    """
    Like httplib.HTTPConnection but stores the request headers.
    Used in HTTPHandler2(), see below.
    """
    def putheader(self, header, value):
        self.request_headers["header_list"].append((header, value))
        httplib.HTTPConnection.putheader(self, header, value)

    def send(self, s):
        self.request_headers["send"] = s
        httplib.HTTPConnection.send(self, s)


class HTTPHandler2(urllib2.HTTPHandler):
    """
    A HTTPHandler which stores the request headers.
    Used HTTPConnection2, see above.
    
    >>> opener = urllib2.build_opener(HTTPHandler2)
    >>> opener.addheaders = [("User-agent", "Python test")]
    >>> response = opener.open('http://www.google.com/')
    
    Get the request headers as a list build with HTTPConnection.putheader():
    >>> response.request_headers
    [('Accept-Encoding', 'identity'), ('Host', 'www.google.de'), ('Connection', 'close'), ('User-Agent', 'Python test')]
    
    >>> response.request_header
    'GET / HTTP/1.1\\r\\nAccept-Encoding: identity\\r\\nHost: www.google.de\\r\\nConnection: close\\r\\nUser-Agent: Python test\\r\\n\\r\\n'
    """
    def http_open(self, req):
        conn_class = HTTPConnection2
        conn_class.request_headers = {"header_list": [], "send": ""}
        response = self.do_open(conn_class, req)
        response.request_headers = conn_class.request_headers["header_list"]
        response.request_header = conn_class.request_headers["send"]
        return response


class HttpRequest(object):
    """
    Helper class for easy request a web page and encode the response into unicode.
    Used HTTPHandler2, so the complete request headers are available.
    
    >>> r = HttpRequest("http://www.heise.de")
    >>> r.request.add_header("User-agent", "Python test")
    >>> response = r.get_response()
       
    List of all headers, used to create the Request:
    >>> response.request_headers
    [('Accept-Encoding', 'identity'), ('Host', 'www.heise.de'), ('Connection', 'close'), ('User-Agent', 'Python test')]
    
    The used Request as Text:
    >>> response.request_header.split("\\r\\n")
    ['GET / HTTP/1.1', 'Accept-Encoding: identity', 'Host: www.heise.de', 'Connection: close', 'User-Agent: Python test', '', '']
       
    
    Get the response httplib.HTTPMessage instance:
    
    >>> info = response.info()
    >>> info["content-type"]
    'text/html; charset=utf-8'

    >>> response.getcode()
    200
    >>> response.geturl()
    'http://www.heise.de'

    
    Get the content in unicode:
    
    >>> content = r.get_unicode()
    >>> isinstance(content, unicode)
    True
    >>> content[:14]
    u'<!DOCTYPE html'
    
    
    If some encodings wrong, these list stored the tried encodings:
    
    >>> r.tried_encodings
    []
    """
    charset_re = None

    def __init__(self, url, timeout=5):
        self.request = urllib2.Request(url=url)
        self.timeout = timeout

        self.opener = urllib2.build_opener(HTTPHandler2)

        # set in get_response()
        self.response_header = None
        self.response = None

        # filled in get_unicode()
        self.tried_encodings = []

    def get_response(self):
        if self.response is None:
            self.response = self.opener.open(self.request)
            self.response_header = self.response.info() # httplib.HTTPMessage instance
        return self.response

    def get_content(self):
        response = self.get_response()
        content = response.read()
        return content

    def get_content_type(self):
        content_type = self.response_header.get("content-type")
        content_type, params = cgi.parse_header(content_type)
        return content_type, params

    def get_encoding_from_content_type(self):
        content_type, params = self.get_content_type()
        if "charset" in params:
            return params["charset"].strip("'\"")

    def get_encodings_from_content(self, content):
        if self.charset_re is None:
            self.charset_re = re.compile(
                r'<meta.*?charset=["\']*(.+?)["\'>]', flags=re.I
            )
        return self.charset_re.findall(content)

    def get_unicode(self):
        """
        Returns the requested content back in unicode.
        Tried:
            1. charset from content-type
            2. every encodings from <meta ... charset=XXX>
            3. fall back and replace all unicode characters
        """
        content = self.get_content()

        # Try charset from content-type
        encoding = self.get_encoding_from_content_type()
        if encoding:
            try:
                return unicode(content, encoding)
            except UnicodeError:
                self.tried_encodings.append(encoding)

        # Try every encodings from <meta ... charset=XXX>
        encodings = self.get_encodings_from_content(content)
        for encoding in encodings:
            if encoding in self.tried_encodings:
                continue
            try:
                return unicode(content, encoding)
            except UnicodeError:
                self.tried_encodings.append(encoding)

        # Fall back:
        return unicode(content, encoding, errors="replace")





if __name__ == "__main__":
    import doctest
    print doctest.testmod()

    r = HttpRequest("http://www.google.de")
    print r.get_unicode()
