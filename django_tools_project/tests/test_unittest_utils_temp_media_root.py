import tempfile
from pathlib import Path

from bx_py_utils.path import assert_is_dir
from cli_base.cli_tools.test_utils.assertion import assert_startswith
from django.conf import settings
from django.test import SimpleTestCase

from django_tools.unittest_utils.temp_media_root import TempMediaRoot


class TempMediaRootTestCase(SimpleTestCase):
    def test_happy_path(self):
        tempdir = tempfile.gettempdir()

        with TempMediaRoot() as media_root_path:
            self.assertIsInstance(media_root_path, Path)
            self.assertTrue(media_root_path.is_absolute())
            assert_is_dir(media_root_path)

            self.assertEqual(settings.MEDIA_ROOT, str(media_root_path))

            # check that's in the temp dir:
            assert_startswith(str(media_root_path), prefix=tempdir)

            Path(media_root_path / 'test.txt').write_text('test')

        self.assertFalse(media_root_path.exists())

        # Works also as decorator:
        @TempMediaRoot()
        def example():
            assert_startswith(settings.MEDIA_ROOT, prefix=tempdir)
