"""
    Add HTML comments with the template name/path
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The rendered templates will have inserted this:
        <!-- START 'foo/bar.html' -->
        ...
        <!-- END 'foo/bar.html' -->

    Usage, e.g.:

    if DEBUG:
        TEMPLATES[0]["OPTIONS"]["loaders"] = [
            (
                "django_tools.template.loader.DebugCacheLoader", (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                )
            )
        ]
"""


from django.template.base import TextNode
from django.template.loaders.cached import Loader as CachedLoader


class BaseDebugTemplateCache(dict):
    def add_tags(self, template):
        """
        Add START, END comments TextNodes in template nodelist.

        :param template: a django.template.base.Template instance
        """
        template.nodelist.insert(0,
                                 TextNode(f"<!-- START '{template.name}' -->\n")
                                 )
        template.nodelist.append(
            TextNode(f"\n<!-- END '{template.name}' -->")
        )


class DebugTemplateCache(BaseDebugTemplateCache):
    def __setitem__(self, key, value):
        try:
            template, origin = value
        except TypeError:
            # e.g.: value is TemplateDoesNotExist class instance ;)
            pass
        else:
            self.add_tags(template)
        dict.__setitem__(self, key, value)


class GetDebugTemplateCache(BaseDebugTemplateCache):
    def __setitem__(self, key, template):
        if hasattr(template, "nodelist"):
            # e.g.: TemplateDoesNotExist class instance didn't has nodelist ;)
            self.add_tags(template)
        dict.__setitem__(self, key, template)


class DebugCacheLoader(CachedLoader):
    """
    Works like the normal cache loader: 'django.template.loaders.cached.Loader'
    but we add the START/END comments to every cached template.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Change the cache to our own dict classes
        self.get_template_cache = GetDebugTemplateCache()
        self.template_cache = DebugTemplateCache()
