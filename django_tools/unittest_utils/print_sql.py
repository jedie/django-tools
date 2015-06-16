# coding: utf-8

"""   
    print SQL
    ~~~~~~~~~
    
    :copyleft: 2012-2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function
from django.db import connections, DEFAULT_DB_ALIAS
from django.utils import six
from django.test.utils import CaptureQueriesContext
from django.utils.encoding import smart_text

PFORMAT_SQL_KEYWORDS = ("FROM", "WHERE", "ORDER BY", "VALUES")

def pformat_sql(sql):
    # remove unicode u''
    sql = sql.replace("u'", "'").replace('u"', '"')

    sql = sql.replace('`', '')
    for keyword in PFORMAT_SQL_KEYWORDS:
        sql = sql.replace(' %s ' % keyword, '\n\t%s ' % keyword)

    return smart_text(sql)


class PrintQueries(CaptureQueriesContext):
    """
    with context manager to print the used SQL Queries.
    usage e.g.:
    ---------------------------------------------------------------------------
    
    from django_tools.unittest_utils.print_sql import PrintQueries
    
    # e.g. use in unittests:
    class MyTests(TestCase):
        def test_foobar(self):
            with PrintQueries("Create object"):
                FooBar.objects.create("name"=foo)
                
    # e.g. use in views:
    def my_view(request):
        with PrintQueries("Create object"):
            FooBar.objects.create("name"=foo)
                
    the output is like:
    ___________________________________________________________________________
     *** Create object ***
    1 - INSERT INTO "foobar" ("name")
        VALUES (foo)
    ---------------------------------------------------------------------------
    """
    def __init__(self, headline, **kwargs):
        self.headline = headline

        if not "connection" in kwargs:
            using = kwargs.pop("using", DEFAULT_DB_ALIAS)
            kwargs["connection"] = connections[using]

        super(PrintQueries, self).__init__(**kwargs)

    def __exit__(self, exc_type, exc_value, traceback):
        super(PrintQueries, self).__exit__(exc_type, exc_value, traceback)
        if exc_type is not None:
            return

        print()
        print("_"*79)
        if self.headline:
            print(" *** %s ***" % self.headline)
        for no, q in enumerate(self.captured_queries, 1):
            sql = pformat_sql(q["sql"])
            msg = smart_text("%i - %s\n" % (no, sql))
            print(msg)
        print("-"*79)



