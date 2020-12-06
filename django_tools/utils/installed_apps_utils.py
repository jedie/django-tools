from importlib import import_module

from django.apps import apps
from django.urls import Resolver404
from django.urls.resolvers import RegexPattern, URLResolver


def get_filtered_apps(resolve_url="/", no_args=True, debug=False, skip_fail=False):
    """
    Create a list of all Apps witch can resolve the given url >resolve_url<

    @param resolve_url: url used for RegexURLResolver
    @param no_args: Only views without args/kwargs ?
    @parm skip_fail: If True: raise exception if app is not importable

    Please look at:

        django_tools.django_tools_tests.test_installed_apps_utils

    with debug, some print messages would be created:

    e.g.: get_filtered_apps(debug=True)
    found 'django.contrib.admindocs' with urls.py
    found 'django.contrib.auth' with urls.py
    Skip 'django.contrib.auth': Can't handle root url.
    found 'django.contrib.flatpages' with urls.py
    ['django.contrib.admindocs']
    """
    root_apps = []
    app_configs = apps.get_app_configs()
    for app_config in app_configs:
        app_pkg = app_config.name
        urls_pkg = f"{app_pkg}.urls"
        try:
            url_mod = import_module(urls_pkg)
        except ImportError as err:
            if debug:
                print(f"Skip {app_pkg!r}: has no urls.py")
            if str(err) == f"No module named '{urls_pkg}'":
                continue
            if not skip_fail:
                raise
        except Exception as err:
            if debug:
                print(f"Error importing {app_pkg!r}: {err}")
            if not skip_fail:
                raise
            else:
                continue

        if debug:
            print(f"found {app_pkg!r} with urls.py")

        try:
            urlpatterns = url_mod.urlpatterns
        except AttributeError:
            if debug:
                print(f"Skip {app_pkg!r}: urls.py has no 'urlpatterns'")
            continue

        resolver = URLResolver(RegexPattern(r'^'), urlpatterns)
        try:
            func, func_args, func_kwargs = resolver.resolve(resolve_url)
        except Resolver404 as err:
            if debug:
                print(f"Skip {app_pkg!r}: Can't handle root url. ({err})")
            continue
        if not no_args or func_args == () and func_kwargs == {}:
            root_apps.append(app_pkg)
    return root_apps
