"""
    :copyleft: 2020 by django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pathlib import Path

from creole.setup_utils import update_rst_readme
from poetry_publish.tests.test_project_setup import test_poetry_check as assert_poetry_check
from poetry_publish.tests.test_project_setup import test_version as assert_version

import django_tools
from django_tools import __version__


PACKAGE_ROOT = Path(django_tools.__file__).parent.parent


def test_version():
    """
    Check if current version exists in README
    Check if current version is in pyproject.toml
    """
    assert_version(package_root=PACKAGE_ROOT, version=__version__)


def test_assert_rst_readme():
    """
    Check if own README.rst is up-to-date with README.creole
    """
    update_rst_readme(
        package_root=PACKAGE_ROOT, version=__version__, filename='README.creole'
    )


def test_poetry_check():
    """
    Test 'poetry check' output.
    """
    assert_poetry_check(package_root=PACKAGE_ROOT)
