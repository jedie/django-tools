from django_tools import __version__


def django_tools_version_string(request):
    return {"version_string": f"v{__version__}"}
