"""
    :created: 23.12.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import filecmp
import logging
from pathlib import Path

from django.core.files.storage import FileSystemStorage

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_is_file


log = logging.getLogger(__name__)


def file_compare(path1, path2):
    log.debug("compare %r vs, %r", path1, path2)
    assert_is_file(path1)
    assert_is_file(path2)

    # check if file refer to same file
    if path1.samefile(path2):
        log.debug("File refer to the same file")
        return True

    # compare file size:
    size1 = path1.stat().st_size
    size2 = path2.stat().st_size
    if size1 != size2:
        log.debug("Not the same file: different file size.")
        return False

    # Compare file content:
    filecmp.clear_cache()  # if we didn't clear the cache: unittests may be failed!
    return filecmp.cmp(str(path1), str(path2), shallow=False)  # str() needed for python 3.5


class OverwriteFileSystemStorage(FileSystemStorage):
    """
    Overwrite existing files. Usage, e.g:

        class ExampleModel(models.Model):
            foo_file = models.FileField(
                storage=OverwriteFileSystemStorage(create_backups=True)
            )
            bar_image = models.ImageField(
                storage=OverwriteFileSystemStorage(create_backups=True)
            )

    Backups:
        * backup made by appending a suffix and sequential number, e.g.:
            * source....: foo.bar
            * backup 1..: foo.bar.bak
            * backup 2..: foo.bar.bak0
            * backup 3..: foo.bar.bak1

    Backup files are only made if file content changed.

    Based on: https://djangosnippets.org/snippets/976/
    see also: https://code.djangoproject.com/ticket/11663
    """

    def __init__(self, *args, create_backups=True, backup_suffix=".bak", **kwargs):
        """
        :param backup: True/False -> create backup before overwrite
        """
        super().__init__(*args, **kwargs)
        self.create_backups = create_backups
        self.backup_suffix = backup_suffix

    def get_available_name(self, name, max_length=None):
        """
        Always return the origin name and never add random characters to get a unique name
        """
        return name

    def get_bak_path(self, full_path):
        for no in range(1, 99):
            bak_path = full_path.with_suffix(f"{full_path.suffix}{self.backup_suffix}{no:02d}")
            if not bak_path.is_file():
                return bak_path

        raise RuntimeError("No free backup filenames!")

    def _save(self, name, content):
        """
        There's a potential race condition here:
        It's possible that two threads might whant to save the same file.
        """
        full_path = Path(self.path(name))

        bak_path = None

        if full_path.is_file():
            if self.create_backups:
                bak_path = self.get_bak_path(full_path)

                log.info("Backup %s -> %s", full_path, bak_path)
                full_path.rename(bak_path)
            else:
                log.info("Remove old file: %s", full_path)
                full_path.unlink()

        # Save content
        name = super()._save(name, content)
        log.warning(repr(content))
        log.debug("Save file as: %r", name)

        if bak_path is not None and file_compare(full_path, bak_path) is True:
            log.info("Remove %r (same file content)", bak_path)
            bak_path.unlink()

        return name
