from pathlib import Path

import pytest

import django_tools
from django_tools.unittest_utils.project_setup import (
    check_editor_config,
    check_project_max_line_length,
    deep_check_max_line_length,
    get_py_max_line_length,
)


PACKAGE_ROOT = Path(django_tools.__file__).parent.parent
CURRENT_MAX_LINE_LENGTH = 100


def test_deep_check_max_line_length():
    deep_check_max_line_length(data={}, max_line_length=0, path=[])
    deep_check_max_line_length(data={'line_length': 100}, max_line_length=100, path=[])
    deep_check_max_line_length(data={'foo': {'line_length': 100}}, max_line_length=100, path=[])

    with pytest.raises(AssertionError) as excinfo:
        deep_check_max_line_length(
            data={'foo': {'bar': {'line_length': 100}}},
            max_line_length=120,
            path=['pyproject.toml'],
        )

    assert (
        str(excinfo.value)
        == "'line_length' in pyproject.toml / foo / bar is 100 but should be 120 !"
    )


def test_get_py_max_line_length():
    assert get_py_max_line_length(package_root=PACKAGE_ROOT) == CURRENT_MAX_LINE_LENGTH


def test_check_project_max_line_length():
    check_project_max_line_length(
        package_root=PACKAGE_ROOT, max_line_length=CURRENT_MAX_LINE_LENGTH
    )

    assert CURRENT_MAX_LINE_LENGTH != 79
    with pytest.raises(AssertionError) as excinfo:
        check_project_max_line_length(package_root=PACKAGE_ROOT, max_line_length=79)
    error_msg = str(excinfo.value)
    assert ' in pyproject.toml ' in error_msg
    assert ' is 100 but should be 79 !' in error_msg


def test_check_editor_config():
    check_editor_config(package_root=PACKAGE_ROOT)

    msg = "Editor config 'foo' for files like foobar.xy is not defined!"
    with pytest.warns(RuntimeWarning, match=msg):
        check_editor_config(
            package_root=PACKAGE_ROOT,
            config_defaults={
                'foobar.xy': {
                    'foo': 'bar',
                },
            },
        )

    msg = "Editor config 'indent_style' for files like foobar.py should be 'tab' but is: 'space'!"
    with pytest.warns(RuntimeWarning, match=msg):
        check_editor_config(
            package_root=PACKAGE_ROOT,
            config_defaults={
                'foobar.py': {
                    'indent_style': 'tab',
                },
            },
        )
