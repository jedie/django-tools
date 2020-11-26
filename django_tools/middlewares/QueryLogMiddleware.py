"""
Print the query log to standard out.

Useful for optimizing database calls.

Inspired by the method at: <http://www.djangosnippets.org/snippets/344/>
"""
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object  # fallback for Django < 1.10


class QueryLogMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        from django.conf import settings
        from django.db import connection

        if settings.DEBUG:
            queries = {}
            for query in connection.queries:
                sql = query["sql"]
                queries.setdefault(sql, 0)
                queries[sql] += 1
            duplicates = sum([count - 1 for count in list(queries.values())])
            print("------------------------------------------------------")
            print(f"Total Queries:     {len(queries)}")
            print(f"Duplicate Queries: {duplicates}")
            print()
            for query, count in list(queries.items()):
                print(f"{count} x {query}")
            print("------------------------------------------------------")
        return response
