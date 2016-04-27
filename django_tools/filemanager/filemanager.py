# coding: utf-8

"""
    filemanager
    ~~~~~~~~~~~

    Stuff to build a app like a file manager.


    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function



from operator import attrgetter
import datetime
import grp
import os
import pwd
import stat

if __name__ == "__main__":
    # For doctest only
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings
    global_settings.SITE_ID = 1

from django.contrib import messages

from django_tools.filemanager.exceptions import FilemanagerError
from django_tools.filemanager.filesystem_browser import BaseFilesystemBrowser
from django_tools.filemanager.utils import symbolic_notation


class BaseFilesystemObject(object):
    def __init__(self, base_path, name, abs_path, link_path=None):
        self.base_path = base_path # path in which this item exists
        self.name = name # The name of the directory item
        self.abs_path = abs_path # absolute path to this dir item
        self.link_path = link_path # Only for links: the real path of the dir item

        self.stat = os.stat(self.abs_path)
        self.size = self.stat[stat.ST_SIZE]
        self.mode = self.stat[stat.ST_MODE]
        self.mtime = datetime.datetime.fromtimestamp(self.stat[stat.ST_MTIME])

        self.mode_octal = oct(self.mode)
        self.mode_symbol = symbolic_notation(self.mode)

        self.uid = self.stat[stat.ST_UID]
        self.username = pwd.getpwuid(self.uid).pw_name
        self.gid = self.stat[stat.ST_GID]
        self.groupname = grp.getgrgid(self.gid).gr_name

    def __repr__(self):
        return "%s '%s' in %s" % (self.item_type, self.name, self.base_path)


class BaseFileItem(BaseFilesystemObject):
    is_file = True
    is_dir = False
    item_type = "file"


class BaseDirItem(BaseFilesystemObject):
    is_file = False
    is_dir = True
    item_type = "dir"


class BaseFileLinkItem(BaseFileItem):
    def __init__(self, *args, **kwargs):
        super(BaseFileLinkItem, self).__init__(*args, **kwargs)
        self.item_type = "file link to %s" % self.link_path

class BaseDirLinkItem(BaseDirItem):
    def __init__(self, *args, **kwargs):
        super(BaseDirLinkItem, self).__init__(*args, **kwargs)
        self.item_type = "dir link to %s" % self.link_path


#------------------------------------------------------------------------------


class BaseFilemanager(BaseFilesystemBrowser):
    """
    Base class for building a filemanager
    """
    DIR_ITEM = BaseDirItem
    FILE_ITEM = BaseFileItem
    DIR_LINK_ITEM = BaseDirLinkItem
    FILE_LINK_ITEM = BaseFileLinkItem

    def __init__(self, request, absolute_path, base_url, rest_url, allow_upload=False):
        super(BaseFilemanager, self).__init__(request, absolute_path, base_url, rest_url)

        self.allow_upload = allow_upload
        self.dir_items = self.read_dir(self.absolute_path)

    def read_dir(self, path):
        dir_items = []
        for item in os.listdir(path):
            item_abs_path = os.path.join(self.absolute_path, item)
            link_path = None
            if os.path.islink(item_abs_path):
                link_path = os.readlink(item_abs_path)
                if os.path.isdir(link_path):
                    item_class = self.DIR_LINK_ITEM
                elif os.path.isfile(link_path):
                    item_class = self.FILE_LINK_ITEM
                else:
                    raise NotImplemented
            elif os.path.isdir(item_abs_path):
                item_class = self.DIR_ITEM
            elif os.path.isfile(item_abs_path):
                item_class = self.FILE_ITEM
            else:
                messages.info(self.request, "unhandled directory item: %r" % self.absolute_path)
                continue

            instance = self.get_filesystem_item_instance(item_class, item, item_abs_path, link_path)
            dir_items.append(instance)

        # sort the dir items by name but directories first
        # http://wiki.python.org/moin/HowTo/Sorting/#Operator_Module_Functions
        dir_items = sorted(dir_items, key=attrgetter('item_type', 'name'))

        return dir_items

    def get_filesystem_item_instance(self, item_class, item, item_abs_path, link_path):
        """
        Good point for overwrite, to add attributes to the filesystem items.
        """
        instance = item_class(self.absolute_path, item, item_abs_path, link_path)
        return instance

    def handle_uploaded_file(self, f):
        if not self.allow_upload:
            raise FilemanagerError("Upload not allowed here!")

        path = os.path.join(self.absolute_path, f.name)
        destination = open(path, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()

        messages.success(self.request,
            "File '%s' (%i Bytes) uploaded to %s" % (f.name, f.size, self.absolute_path)
        )


if __name__ == "__main__":
    import doctest
    print(doctest.testmod(
#        verbose=True
        verbose=False
    ))
