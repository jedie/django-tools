import warnings
from pathlib import Path

from django_tools.unittest_utils.assertments import assert_is_dir, assert_is_file


EDITOR_CONFIG_DEFAULTS = {
    'foobar.py': {
        'indent_style': 'space',
        'indent_size': '4',
        'end_of_line': 'lf',
        'charset': 'utf-8',
    },
    'Makefile': {'indent_style': 'tab'},
}


def deep_check_max_line_length(data: dict, max_line_length: int, path: list):
    assert isinstance(data, dict)
    for key, value in data.items():
        if key in ('line_length', 'max_line_length'):
            assert (
                value == max_line_length
            ), f'{key!r} in {" / ".join(path)} is {value!r} but should be {max_line_length} !'

        if isinstance(value, dict):
            deep_check_max_line_length(value, max_line_length, path=[*path, key])


def check_project_max_line_length(package_root, max_line_length: int):
    assert_is_dir(package_root)

    assert isinstance(max_line_length, int)
    assert 70 < max_line_length < 200

    try:
        import tomli
    except ImportError as err:
        raise ImportError(f'Please add "tomli" to your dev-dependencies! Origin error: {err}')

    pyproject_toml = package_root / 'pyproject.toml'
    if pyproject_toml.is_file():
        pyproject_text = pyproject_toml.read_text(encoding="utf-8")
        pyproject_config = tomli.loads(pyproject_text)
        deep_check_max_line_length(pyproject_config, max_line_length, path=['pyproject.toml'])


def _get_editor_config_options(file_path):
    try:
        from editorconfig import get_properties
    except ImportError as err:
        raise ImportError(
            f'Please add "EditorConfig" to your dev-dependencies! Origin error: {err}'
        )

    options = get_properties(file_path)
    return options


def get_py_max_line_length(package_root) -> int:
    options = _get_editor_config_options(package_root / 'foobar.py')
    try:
        max_line_length = int(options['max_line_length'])
    except KeyError:
        raise KeyError('Editor config for Python files does not define "max_line_length" !')
    return max_line_length


def check_editor_config(package_root: Path, config_defaults=None) -> None:
    assert_is_dir(package_root)

    if config_defaults is None:
        config_defaults = EDITOR_CONFIG_DEFAULTS

    conf_filename = '.editorconfig'
    editor_config_file = package_root / conf_filename
    assert_is_file(editor_config_file)

    for example_filename, defaults in config_defaults.items():
        options = _get_editor_config_options(package_root / example_filename)
        for key, value in defaults.items():
            if key not in options:
                warnings.warn(
                    f'Editor config {key!r} for files like {example_filename} is not defined!',
                    RuntimeWarning,
                )
            else:
                current_value = options[key]
                if current_value != value:
                    warnings.warn(
                        (
                            f'Editor config {key!r} for files like {example_filename}'
                            f' should be {value!r} but is: {current_value!r}!'
                        ),
                        RuntimeWarning,
                    )

    max_line_length = get_py_max_line_length(package_root)
    check_project_max_line_length(package_root, max_line_length)
