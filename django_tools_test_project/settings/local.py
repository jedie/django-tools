"""
    Settings for local dev server run
"""

from django_tools_test_project.settings.base import *  # noqa


print("Use settings:", __file__)

MIDDLEWARE = list(MIDDLEWARE) + [  # noqa
    "django_tools.middlewares.local_auto_login.AlwaysLoggedInAsSuperUserMiddleware",
]
