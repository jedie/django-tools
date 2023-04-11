from pathlib import Path

from django.test import TestCase

import django_tools
from django_tools.unittest_utils.project_setup import (
    check_editor_config,
    check_project_max_line_length,
    deep_check_max_line_length,
    get_py_max_line_length,
)


PACKAGE_ROOT = Path(django_tools.__file__).parent.parent
CURRENT_MAX_LINE_LENGTH = 100


class UnittestUtilsProjectSetupTestCase(TestCase):
    def test_deep_check_max_line_length(self):
        deep_check_max_line_length(data={}, max_line_length=0, path=[])
        deep_check_max_line_length(data={'line_length': 100}, max_line_length=100, path=[])
        deep_check_max_line_length(data={'foo': {'line_length': 100}}, max_line_length=100, path=[])

        with self.assertRaisesMessage(
            AssertionError, "'line_length' in pyproject.toml / foo / bar is 100 but should be 120 !"
        ):
            deep_check_max_line_length(
                data={'foo': {'bar': {'line_length': 100}}},
                max_line_length=120,
                path=['pyproject.toml'],
            )

    def test_get_py_max_line_length(self):
        assert get_py_max_line_length(package_root=PACKAGE_ROOT) == CURRENT_MAX_LINE_LENGTH

    def test_check_project_max_line_length(self):
        check_project_max_line_length(package_root=PACKAGE_ROOT, max_line_length=CURRENT_MAX_LINE_LENGTH)

        assert CURRENT_MAX_LINE_LENGTH != 79
        with self.assertRaisesMessage(AssertionError, ' is 100 but should be 79 !'):
            check_project_max_line_length(package_root=PACKAGE_ROOT, max_line_length=79)

    def test_check_editor_config(self):
        check_editor_config(package_root=PACKAGE_ROOT)

        with self.assertRaisesMessage(
            RuntimeWarning,
            "Editor config 'indent_style' for files like foobar.py should be 'tab' but is: 'space'!",
        ):
            check_editor_config(
                package_root=PACKAGE_ROOT,
                config_defaults={
                    'foobar.xy': {
                        'foo': 'bar',
                    },
                },
            )

        with self.assertRaisesMessage(RuntimeWarning, "Editor config 'foo' for files like foobar.xy is not defined!"):
            check_editor_config(
                package_root=PACKAGE_ROOT,
                config_defaults={
                    'foobar.py': {
                        'indent_style': 'tab',
                    },
                },
            )
