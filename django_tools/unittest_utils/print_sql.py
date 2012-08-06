# coding: utf-8

"""   
    print SQL
    ~~~~~~~~~
    
    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.db import connections, DEFAULT_DB_ALIAS, reset_queries
from django.core.signals import request_started

PFORMAT_SQL_KEYWORDS = ("FROM", "WHERE", "ORDER BY", "VALUES")

def pformat_sql(sql):
    sql = sql.replace('`', '')
    for keyword in PFORMAT_SQL_KEYWORDS:
        sql = sql.replace(' %s ' % keyword, '\n\t%s ' % keyword)
    return sql

class PrintQueries(object):
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
    def __init__(self, msg="", using=None):
        self.msg = msg

        if using is None:
            using = DEFAULT_DB_ALIAS
        self.connection = connections[using]

    def __enter__(self):
        self.old_debug_cursor = self.connection.use_debug_cursor
        self.connection.use_debug_cursor = True
        self.starting_queries = len(self.connection.queries)
        request_started.disconnect(reset_queries)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.use_debug_cursor = self.old_debug_cursor
        request_started.connect(reset_queries)
        if exc_type is not None:
            return

        final_queries = len(self.connection.queries)
        executed = final_queries - self.starting_queries

        print
        print "_"*79
        if self.msg:
            print " *** %s ***" % self.msg
        for no, q in enumerate(self.connection.queries[-executed:], 1):
            print "%i - %s" % (no, pformat_sql(q["sql"]))
            print
        print "-"*79
