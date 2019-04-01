"""
    :created: 28.08.2018 by Jens Diemer
    :copyleft: 2018-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import textwrap
from pathlib import Path

from django.conf import settings
from django.core import mail
from django.core.mail import get_connection

import icdiff
import pprintpp


def assert_startswith(text, prefix):
    """
    Check if test starts with prefix.
    """
    assert text.startswith(prefix), "%r doesn't starts with %r" % (text, prefix)


def assert_endswith(text, suffix):
    """
    Check if text ends with suffix.
    """
    assert text.endswith(suffix), "%r doesn't ends with %r" % (text, suffix)


def assert_locmem_mail_backend():
    """
    Check if current email backend is the In-memory backend.
    See:
        https://docs.djangoproject.com/en/1.11/topics/email/#in-memory-backend
    """
    mail_backend = get_connection()
    assert isinstance(mail_backend, mail.backends.locmem.EmailBackend), "Wrong backend: %s" % mail_backend


def assert_language_code(*, language_code):
    """
    Check if given language_code is in settings.LANGUAGES
    """
    existing_language_codes = tuple(dict(settings.LANGUAGES).keys())
    assert language_code in existing_language_codes, "%r not in settings.LANGUAGES=%r" % (
        language_code,
        settings.LANGUAGES,
    )


def assert_installed_apps(*, app_names):
    """
    Check entries in settings.INSTALLED_APPS
    """
    assert isinstance(app_names, (tuple, list))
    installed_apps = settings.INSTALLED_APPS
    for app_name in app_names:
        assert app_name in installed_apps, "%r not in settings.INSTALLED_APPS!" % app_name


def assert_is_dir(path):
    """
    Check if given path is a directory
    """
    if not isinstance(path, Path):
        path = Path(path)
    assert path.is_dir(), "Directory not exists: %s" % path


def assert_is_file(path):
    """
    Check if given path is a file
    """
    if not isinstance(path, Path):
        path = Path(path)
    assert_is_dir(path.parent)
    assert path.is_file(), "File not exists: %s" % path


def assert_path_not_exists(path):
    """
    Check if given path doesn't exists
    """
    if not isinstance(path, Path):
        path = Path(path)

    assert not path.is_dir(), "Path is a existing directory: %s" % path
    assert not path.is_file(), "Path is a existing file: %s" % path
    assert not path.is_fifo(), "Path is a existing fifo: %s" % path
    assert not path.exists(), "Path exists: %s" % path


def pformat(obj, indent=4, width=100):
    pformat_return_list = pprintpp.pformat(obj, indent=indent, width=width)
    return pformat_return_list.splitlines()


def create_icdiff(first, second, fromfile="first", tofile="second", indent=4, width=100):
    """
    Based on:
        https://github.com/hjwp/pytest-icdiff/blob/master/pytest_icdiff.py
    """
    if isinstance(first, str):
        first = first.splitlines()
    else:
        first = pformat(first, indent=indent, width=width)

    if isinstance(second, str):
        second = second.splitlines()
    else:
        second = pformat(second, indent=indent, width=width)

    icdiff_lines = list(
        icdiff.ConsoleDiff(tabsize=2, cols=width, highlight=True).make_table(
            fromlines=first, tolines=second, fromdesc=fromfile, todesc=tofile
        )
    )
    if len(icdiff_lines) == 1:
        # hacky whitespace reduce:
        icdiff_lines[0] = icdiff_lines[0].replace("        ", " ")

    # icdiff_lines = [f"{COLOR_OFF}{l}" for l in icdiff_lines]

    return "\n".join(icdiff_lines)


def assert_pformat_equal(first, second, msg="", **pformat_kwargs):
    """ compare with pprintpp and icdiff output """
    if first != second:
        if isinstance(first, str):
            print(first)
        else:
            pprintpp.pprint(first, **pformat_kwargs)
        assert first == second, "%s%s" % (msg, create_icdiff(first=first, second=second, **pformat_kwargs))


def dedent(txt):
    # Remove any common leading whitespace from every line
    txt = textwrap.dedent(txt)

    # strip whitespace at the end of every line
    txt = "\n".join([line.rstrip() for line in txt.splitlines()])
    txt = txt.strip()
    return txt


def assert_equal_dedent(first, second, msg=""):
    assert_pformat_equal(dedent(first), dedent(second), msg=msg)


def assert_in_dedent(member, container):
    member = dedent(member)
    container = dedent(container)
    assert member in container, "%r not found in %r" % (member, container)


def assert_filenames_and_content(*, path, reference, fromfile="current", tofile="reference", **pformat_kwargs):
    if not isinstance(path, Path):
        path = Path(path)

    assert_is_dir(path)

    current_data = []
    for item in sorted(path.iterdir()):
        with item.open("rb") as f:
            current_data.append((item.name, f.read()))

    if current_data != reference:
        print("\nCurrent filenames and content:")
        pprintpp.pprint(current_data, **pformat_kwargs)

    assert_pformat_equal(current_data, reference, fromfile=fromfile, tofile=tofile, **pformat_kwargs)
