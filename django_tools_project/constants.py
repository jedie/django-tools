from pathlib import Path

from bx_py_utils.path import assert_is_file

import django_tools


PACKAGE_ROOT = Path(django_tools.__file__).parent.parent
assert_is_file(PACKAGE_ROOT / 'pyproject.toml')
