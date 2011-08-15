# encoding: utf-8

"""
    http utils
    ~~~~~~~~~~
    
    Small helpers around getting a webpage via http GET.
    
    You can easy get a web page encoding in unicode with HttpRequest().
    
    HttpRequest() and HTTPHandler2() make it possible to get the complete
    sended request headers. See also:
    http://stackoverflow.com/questions/603856/get-urllib2-request-headers
    
    examples:
    ~~~~~~~~~
    
    Get a page as unicode:
        from django_tools.utils.http import HttpRequest
        r = HttpRequest("http://www.google.com")
        print r.get_unicode()
        
    Get the request/response headers:
        from django_tools.utils.http import HttpRequest
        r = HttpRequest("http://www.google.com")
        response = r.get_response()
        print "Request headers as list:", response.request_headers
        print "Raw Request header:", response.request_header
    
    more info, see DocStrings below...
    
    :copyleft: 2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import cgi
import httplib
import re
import socket
import urllib2


class HTTPConnection2(httplib.HTTPConnection):
    """
    Like httplib.HTTPConnection but stores the request headers.
    Used in HTTPConnection3(), see below.
    """
    def __init__(self, *args, **kwargs):
        httplib.HTTPConnection.__init__(self, *args, **kwargs)
        self.request_headers = []
        self.request_header = ""

    def putheader(self, header, value):
        self.request_headers.append((header, value))
        httplib.HTTPConnection.putheader(self, header, value)

    def send(self, s):
        self.request_header = s
        httplib.HTTPConnection.send(self, s)

if hasattr(httplib, 'HTTPS'):
    class HTTPSConnection2(httplib.HTTPSConnection):
        """
        Like httplib.HTTPConnection but stores the request headers.
        Used in HTTPConnection3(), see below.
        """
        def __init__(self, *args, **kwargs):
            httplib.HTTPSConnection.__init__(self, *args, **kwargs)
            self.request_headers = []
            self.request_header = ""

        def putheader(self, header, value):
            self.request_headers.append((header, value))
            httplib.HTTPSConnection.putheader(self, header, value)

        def send(self, s):
            self.request_header = s
            httplib.HTTPSConnection.send(self, s)


class HTTPConnectionWrapper(object):
    """
    Wrapper around HTTPConnection2
    Used in HTTPHandler2(), see below.
    """
    def __init__(self, conn_class):
        self._conn_class = conn_class

    def __call__(self, *args, **kwargs):
        """
        instance made in urllib2.HTTPHandler.do_open()
        """
        self._conn = self._conn_class(*args, **kwargs)
        self.request_headers = self._conn.request_headers
        self.request_header = self._conn.request_header
        return self

    def __getattribute__(self, name):
        """
        Redirect attribute access to the local HTTPConnection() instance.
        """
        if name in ("_conn", "_conn_class"):
            return object.__getattribute__(self, name)
        else:
            return getattr(self._conn, name)


class HTTPHandler2(urllib2.HTTPHandler):
    """
    A HTTPHandler which stores the request headers.
    Used HTTPConnection3, see above.
    
    >>> opener = urllib2.build_opener(HTTPHandler2)
    >>> opener.addheaders = [("User-agent", "Python test")]
    >>> response = opener.open('http://www.python.org/')
   
    Get the request headers as a list build with HTTPConnection.putheader():
    >>> response.request_headers
    [('Accept-Encoding', 'identity'), ('Host', 'www.python.org'), ('Connection', 'close'), ('User-Agent', 'Python test')]
   
    >>> response.request_header.split("\\r\\n")[0]
    'GET / HTTP/1.1'
    """
    def http_open(self, req):
        conn_instance = HTTPConnectionWrapper(HTTPConnection2)
        response = self.do_open(conn_instance, req)
        response.request_headers = conn_instance.request_headers
        response.request_header = conn_instance.request_header
        return response

if hasattr(httplib, 'HTTPS'):
    class HTTPSHandler2(urllib2.HTTPSHandler):
        def https_open(self, req):
            conn_instance = HTTPConnectionWrapper(HTTPSConnection2)
            response = self.do_open(conn_instance, req)
            response.request_headers = conn_instance.request_headers
            response.request_header = conn_instance.request_header
            return response


class HttpRequest(object):
    """
    Helper class for easy request a web page and encode the response into unicode.
    Used HTTPHandler2, so the complete request headers are available.
    
    timeout
    ~~~~~~~
    HttpRequest() can take the argument 'timeout' but this works only since Python 2.6
    For Python < 2.6 the timeout TypeError would be silently catch.
    Activate a work-a-round with 'threadunsafe_workaround' to use socket.setdefaulttimeout()
    But this is not thread-safty!
    more info: 
        http://kurtmckee.livejournal.com/32616.html (Supporting a timeout in feedparser)
    
    examples
    ~~~~~~~~
    
    >>> r = HttpRequest("http://www.heise.de")
    >>> r.request.add_header("User-agent", "Python test")
    >>> response = r.get_response()
       
    List of all headers, used to create the Request:
    >>> response.request_headers
    [('Accept-Encoding', 'identity'), ('Host', 'www.heise.de'), ('Connection', 'close'), ('User-Agent', 'Python test')]
    
    The used Request as Text:
    >>> response.request_header.split("\\r\\n")[0]
    'GET / HTTP/1.1'
           
    
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
    >>> content[:14].lower()
    u'<!doctype html'
    
    
    If some encodings wrong, these list stored the tried encodings:
    
    >>> r.tried_encodings
    []
    
    
    Work's with https, too:
    >>> r = HttpRequest("https://encrypted.google.com")
    >>> r.request.add_header("User-agent", "Python https test")
    >>> content = r.get_unicode()
    >>> isinstance(content, unicode)
    True
    >>> content[:14].lower()
    u'<!doctype html'
    >>> response.request_header.split("\\r\\n")[0]
    'GET / HTTP/1.1'
    """
    _charset_re = None

    def __init__(self, url, timeout=None, threadunsafe_workaround=False):
        self.request = urllib2.Request(url=url)
        self.timeout = timeout
        self.threadunsafe_workaround = threadunsafe_workaround

        handlers = [HTTPHandler2]
        if hasattr(httplib, 'HTTPS'):
            handlers.append(HTTPSHandler2)

        self.opener = urllib2.build_opener(*handlers)

        # set in get_response()
        self.response_header = None
        self.response = None

        # filled in get_unicode()
        self.tried_encodings = []

    def get_response(self):
        """
        Cached access to response object.
        """
        if self.response is None:
            try:
                self.response = self.opener.open(self.request, timeout=self.timeout)
            except TypeError, err:
                # timeout argument is new since Python v2.6
                if not "timeout" in str(err):
                    raise

                if self.threadunsafe_workaround:
                    # set global socket timeout
                    old_timeout = socket.getdefaulttimeout()
                    socket.setdefaulttimeout(self.timeout)

                self.response = self.opener.open(self.request)

                if self.threadunsafe_workaround:
                    # restore global socket timeout
                    socket.setdefaulttimeout(old_timeout)

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
        if self._charset_re is None:
            self._charset_re = re.compile(
                r'<meta.*?charset=["\']*(.+?)["\'>]', flags=re.I
            )
        return self._charset_re.findall(content)

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
    print "Run doctests..."
    import doctest
    print doctest.testmod()
    print "-"*79

    r = HttpRequest("http://www.python.org/index.html", timeout=3, threadunsafe_workaround=True)
    response = r.get_response()
    print response.request_header
    print response.info()
    print repr(r.get_unicode())

    print "-"*79

    r = HttpRequest("https://raw.github.com/jedie/django-tools/master/README.creole", timeout=3, threadunsafe_workaround=True)
    r.request.add_header("User-agent", "Python test")
    r.request.add_header("Referer", "/")
    response = r.get_response()
    print response.request_header
    print response.info()
    print repr(r.get_unicode())
