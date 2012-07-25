# coding: utf-8

"""
    we add the committer date to the version number by a .gitattributes filter
    
    more info about this here:
    https://github.com/jedie/python-code-snippets/tree/master/CodeSnippets/git/#readme
"""


import re


__version__ = (0, 24, 3)


COMMITTER_DATE = "$date$" # set by .gitattributes filter
DATE_REGEX = re.compile(r"\$date:(.*?)\$")

__version__ += (DATE_REGEX.findall(COMMITTER_DATE)[0],)
VERSION_STRING = '.'.join(str(part) for part in __version__)


if __name__ == "__main__":
    print "django-tools v%s" % VERSION_STRING
