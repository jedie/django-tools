# coding: utf-8

"""
    some utils around url
    ~~~~~~~~~~~~~~~~~~~~~

    :created: by Jens Diemer
    :copyleft: 2017 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

from django.http import QueryDict
from django.utils.encoding import force_bytes
from django.utils.six.moves.urllib.parse import quote


class GetDict(QueryDict):
    """
    Similar to origin django.http.QueryDict but:
        - always mutable
        - urlencode() output changed (see DocString there)
    """
    def __init__(self, *args, **kwargs):
        kwargs["mutable"]=True
        super(GetDict, self).__init__(*args, **kwargs)

    def _encode(self, k, v, safe=None):
        if safe is None:
            safe=""

        if v is None:
            return quote(k, safe)

        v = force_bytes(v, self.encoding)
        return '%s=%s' % ((quote(k, safe), quote(v, safe)))

    def urlencode(self, safe=None):
        """
        Same as django.http.QueryDict.urlencode() but:
            - None values will be a empty GET parameter "?empty" (Django: "?empty=")
            - output will be sorted (easier for tests ;)
        """
        output = []
        for k, list_ in sorted(self.lists()):
            k = force_bytes(k, self.encoding)
            output.extend(
                self._encode(k, v, safe)
                for v in sorted(list_)
            )
        return '&'.join(output)


