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


def get_filtered_apps(resolve_url="/", no_args=True, debug=False, skip_fail=False):
    """
    Filter settings.INSTALLED_APPS and create a list
    of all Apps witch can resolve the given url >resolve_url<

    @param resolve_url: url used for RegexURLResolver
    @param no_args: Only views without args/kwargs ?
    @parm skip_fail: If True: raise excaption if app is not importable
    
    >>> get_filtered_apps()
    ['django.contrib.admindocs']
    
    >>> get_filtered_apps(no_args=False)
    ['django.contrib.admindocs', 'django.contrib.flatpages']
    
    >>> get_filtered_apps(debug=True)
    found 'django.contrib.admindocs' with urls.py
    found 'django.contrib.auth' with urls.py
    Skip 'django.contrib.auth': Can't handle root url.
    found 'django.contrib.flatpages' with urls.py
    ['django.contrib.admindocs']
    """
    root_apps = []
    for app_label in settings.INSTALLED_APPS:
        urls_pkg = "%s.urls" % app_label
        try:
            url_mod = import_module(urls_pkg)
        except ImportError, err:
            if debug:
                print "Skip %r: has no urls.py" % app_label
            if str(err) == "No module named urls":
                continue
            if not skip_fail:
                raise
        except Exception, err:
            if debug:
                print "Error importing %r: %s" % (app_label, err)
            if not skip_fail:
                raise
            else:
                continue


        if debug:
            print "found %r with urls.py" % app_label

        try:
            urlpatterns = url_mod.urlpatterns
        except AttributeError:
            if debug:
                print "Skip %r: urls.py has no 'urlpatterns'" % app_label
            continue

        resolver = urlresolvers.RegexURLResolver(r'^/', urlpatterns)
        try:
            func, func_args, func_kwargs = resolver.resolve(resolve_url)
        except urlresolvers.Resolver404, err:
            if debug:
                print "Skip %r: Can't handle root url." % app_label
            continue
        if not no_args or func_args == () and func_kwargs == {}:
            root_apps.append(app_label)
    return root_apps


if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
