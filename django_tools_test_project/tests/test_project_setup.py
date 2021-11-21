"""
    :copyleft: 2020 by django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import re
import subprocess
from pathlib import Path

from creole.setup_utils import update_rst_readme
from poetry_publish.tests.test_project_setup import test_poetry_check as assert_poetry_check
from poetry_publish.tests.test_project_setup import test_version as assert_version

import django_tools
from django_tools import __version__


PACKAGE_ROOT = Path(django_tools.__file__).parent.parent


def strip_style(text):
    """
    Strip ANSI style sequences
    """
    return re.sub(r'\x1b\[[^m]*m', '', text)


def test_version():
    """
    Check if current version exists in README
    Check if current version is in pyproject.toml
    """
    assert_version(package_root=PACKAGE_ROOT, version=__version__)


def test_make_help_up2date():
    completed_process = subprocess.run(
        ['make'], cwd=PACKAGE_ROOT, text=True, capture_output=True,
        check=True, timeout=5,
    )
    help_text = strip_style(completed_process.stdout.strip())

    lines = help_text.splitlines()
    if '/django-tools' in lines[0]:
        # make output if not in same directory ;)
        help_text = '\n'.join(lines[1:-1])

    readme_content = Path(PACKAGE_ROOT, 'README.creole').read_text()
    if help_text not in readme_content:
        print('-' * 100)
        print(help_text)  # for easy copy&paste ;)
        print('-' * 100)
        raise AssertionError(f'README.creole not up2date, missing:\n{help_text}')


def test_update_rst_readme(capsys):
    rest_readme_path = update_rst_readme(
        package_root=PACKAGE_ROOT, filename='README.creole'
    )
    captured = capsys.readouterr()
    assert captured.out == 'Generate README.rst from README.creole...nothing changed, ok.\n'
    assert captured.err == ''
    assert isinstance(rest_readme_path, Path)
    assert str(rest_readme_path).endswith('/README.rst')


def test_poetry_check():
    """
    Test 'poetry check' output.
    """
    assert_poetry_check(package_root=PACKAGE_ROOT)


def test_lint():
    subprocess.check_call(['make', 'fix-code-style'], cwd=PACKAGE_ROOT)
