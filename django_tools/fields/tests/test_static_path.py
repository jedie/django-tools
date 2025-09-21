import tempfile
from pathlib import Path

from django.test import TestCase, override_settings

from django_tools.fields.static_path import StaticPathWidget


class StaticPathWidgetTestCase(TestCase):
    def test_choices(self):
        with tempfile.TemporaryDirectory() as temp_dir, override_settings(STATIC_ROOT=temp_dir):
            temp_path = Path(temp_dir)

            # Empty:
            self.assertEqual(StaticPathWidget().choices, [])

            # Files has no effect:
            (temp_path / 'test1.txt').touch()
            (temp_path / 'test2.txt').touch()
            self.assertEqual(StaticPathWidget().choices, [])

            sub_path1 = temp_path / 'sub 1'
            sub_path1.mkdir()
            (sub_path1 / 'sub1_file1.txt').touch()
            (sub_path1 / 'sub1_file2.txt').touch()

            sub_path2 = temp_path / 'Sub 2'
            sub_path2.mkdir()
            (sub_path2 / 'Sub2_file.txt').touch()

            (temp_path / 'sub 3').mkdir()
            (temp_path / 'sub 3' / 'Sub sub 1').mkdir()
            (temp_path / 'sub 3' / 'sub sub 2').mkdir()

            self.assertEqual(
                StaticPathWidget().choices,
                [
                    ('sub 1', 'sub 1'),
                    ('Sub 2', 'Sub 2'),
                    ('sub 3', 'sub 3'),
                    ('sub 3/Sub sub 1', 'sub 3/Sub sub 1'),
                    ('sub 3/sub sub 2', 'sub 3/sub sub 2'),
                ],
            )
