# coding:utf-8

if __name__ == "__main__":
    print "run doctest:"
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings
    global_settings.INSTALLED_APPS += (
        'django.contrib.admindocs',
        'django.contrib.auth',
        'django.contrib.flatpages',
    )

from django.conf import settings
from django.core import urlresolvers
from django.utils.importlib import import_module

def get_filtered_apps(resolve_url="/"):
    """
    Filter settings.INSTALLED_APPS and create a list
    of all Apps witch can resolve the given url >resolve_url<
    
    >>> get_filtered_apps()
    ['django.contrib.admindocs']
    """
    root_apps = []
    for app_label in settings.INSTALLED_APPS:
        urls_pkg = "%s.urls" % app_label
        try:
            url_mod = import_module(urls_pkg)
        except ImportError, err:
            if str(err) == "No module named urls":
                continue
            raise

        try:
            urlpatterns = url_mod.urlpatterns
        except AttributeError:
            continue

        resolver = urlresolvers.RegexURLResolver(r'^/', urlpatterns)
        try:
            func, func_args, func_kwargs = resolver.resolve(resolve_url)
        except urlresolvers.Resolver404:
            continue

        if func_args == () and func_kwargs == {}:
            root_apps.append(app_label)
    return root_apps

if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
