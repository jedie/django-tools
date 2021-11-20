"""
    :created: 23.12.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import shutil
from pathlib import Path

from django.core.files.uploadedfile import TemporaryUploadedFile
from django.test import TestCase

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_filenames_and_content, assert_is_file
from django_tools_test_project.django_tools_test_app.models import (
    OverwriteFileSystemStorageModel,
    temp_storage_location,
)


class FileSystemStorageTestCase(TestCase):
    def setUp(self):
        super().setUp()
        Path(temp_storage_location).mkdir(mode=0o777, parents=True, exist_ok=True)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(temp_storage_location, ignore_errors=True)

    def test_basic_save(self):
        with TemporaryUploadedFile("test_basic_save.txt", "text/plain", 0, "UTF-8") as tmp_file:
            instance = OverwriteFileSystemStorageModel.objects.create(file=tmp_file)

        print(instance.file.path)
        assert_is_file(instance.file.path)
        assert instance.file.name == "test_basic_save.txt"

        assert_filenames_and_content(path=temp_storage_location, reference=[("test_basic_save.txt", b"")])

    def test_backup_only_one_time(self):
        for i in range(4):
            with TemporaryUploadedFile("test_backup_only_one_time.txt", "text/plain", 0, "UTF-8") as tmp_file:
                instance = OverwriteFileSystemStorageModel.objects.create(file=tmp_file)

        assert_is_file(instance.file.path)
        assert instance.file.name == "test_backup_only_one_time.txt"

        assert_filenames_and_content(path=temp_storage_location, reference=[("test_backup_only_one_time.txt", b"")])

    def test_backup(self):
        with TemporaryUploadedFile("test_backup.txt", "text/plain", 0, "UTF-8") as tmp_file:
            tmp_file.write(b"content one")
            tmp_file.flush()
            tmp_file.seek(0)
            instance1 = OverwriteFileSystemStorageModel.objects.create(file=tmp_file)

        # create a second instance with the same filename and different content:

        with TemporaryUploadedFile("test_backup.txt", "text/plain", 0, "UTF-8") as tmp_file:
            tmp_file.write(b"content two")
            tmp_file.flush()
            tmp_file.seek(0)
            instance2 = OverwriteFileSystemStorageModel.objects.create(file=tmp_file)

        assert_is_file(instance1.file.path)
        assert_is_file(instance2.file.path)

        assert instance1.file.path == instance2.file.path
        assert instance1.file.name == "test_backup.txt"
        assert instance2.file.name == "test_backup.txt"

        assert_filenames_and_content(
            path=temp_storage_location,
            reference=[("test_backup.txt", b"content two"), ("test_backup.txt.bak01", b"content one")],
        )

    def test_backups(self):

        from django_tools.file_storage.file_system_storage import log as origin_log

        def log_temp_storage_location():
            for no, item in enumerate(sorted(Path(temp_storage_location).iterdir()), 1):
                with item.open("rb") as f:
                    origin_log.info("\t%i %s -> %r", no, item, repr(f.read()))

        for content_no in range(1, 7):
            # Save 4 times different content
            content = f"content {content_no:d}"
            for file_no in range(1, 5):
                origin_log.critical("_" * 100)
                origin_log.critical("Save %r for %i time(s)", content, file_no)

                with TemporaryUploadedFile("same_filename.txt", "text/plain", 0, "UTF-8") as tmp_file:
                    tmp_file.write(bytes(content, "utf-8"))
                    tmp_file.flush()
                    tmp_file.seek(0)
                    instance = OverwriteFileSystemStorageModel.objects.create(file=tmp_file)
                    print(repr(instance))

            log_temp_storage_location()

        print(instance.file.path)
        assert_is_file(instance.file.path)
        assert instance.file.name == "same_filename.txt"

        assert_filenames_and_content(
            path=temp_storage_location,
            reference=[
                ("same_filename.txt", b"content 6"),
                ("same_filename.txt.bak01", b"content 1"),
                ("same_filename.txt.bak02", b"content 2"),
                ("same_filename.txt.bak03", b"content 3"),
                ("same_filename.txt.bak04", b"content 4"),
                ("same_filename.txt.bak05", b"content 5"),
            ],
        )
