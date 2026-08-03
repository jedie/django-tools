"""
    DjangoCommandMixin
    ~~~~~~~~~~~~~~~~~~

    :copyleft: 2012-2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import pprint
import subprocess
import sys
from pathlib import Path

from bx_py_utils.path import assert_is_dir
from cli_base.cli_tools.test_utils.rich_test_utils import BASE_WIDTH, get_fixed_env_copy, strip_ansi_codes


class DjangoCommandMixin:
    def call_manage_py(
        self,
        cmd,
        manage_dir,
        manage_py='manage.py',
        assert_executable=True,
        width: int = BASE_WIDTH,
        strip_line_prefix: str = 'django-tools-project v',  # Should be set to project prefix to skip header lines
        strip_ansi: bool = True,
        debug=False,
        excepted_exit_code=0,
        **kwargs,
    ):
        """
        call manage.py from given >manage_dir<
        """
        assert isinstance(cmd, (list, tuple)), f'{cmd=}'

        test_path = Path(manage_dir) / manage_py
        if not test_path.is_file():
            raise AssertionError(f"File doesn't exists: {manage_dir!r} (given <manage_dir> path wrong?!?)")

        if assert_executable and not os.access(test_path, os.X_OK):
            raise AssertionError(f'Manage file {test_path!r} is not executable!')

        if 'env' not in kwargs:
            # e.g.: transfer DJANGO_SETTINGS_MODULE ;)
            kwargs['env'] = os.environ.copy()

        kwargs['env'].update(get_fixed_env_copy(width=width, exclude_none=True))
        kwargs['env']['NO_AUTO_UV_UPGRADE'] = '1'  # Speedup: Disable auto uv upgrade in manage.py
        kwargs['cwd'] = manage_dir

        cmd = [sys.executable, manage_py] + list(cmd)

        subprocess_kwargs = {
            'text': True,
            'stderr': subprocess.STDOUT,
        }
        subprocess_kwargs.update(kwargs)
        if 'cwd' in subprocess_kwargs:
            cwd = subprocess_kwargs['cwd']
            assert_is_dir(cwd)
            if debug:
                print(f'DEBUG: cwd {cwd!r}, ok')

        try:
            stdout = subprocess.check_output(cmd, **subprocess_kwargs)
            status = 0
        except subprocess.CalledProcessError as ex:
            stdout = ex.output
            status = ex.returncode

        if strip_ansi:
            stdout = strip_ansi_codes(stdout)

        if (excepted_exit_code is not None and status != excepted_exit_code) or debug:
            msg = (
                f'subprocess exist status == {status!r} (excepted: {excepted_exit_code!r})\n'
                f'Call {cmd!r} with:\n'
                f'{pprint.pformat(subprocess_kwargs)}\n'
                'subprocess output:\n'
                '------------------------------------------------------------\n'
                f'{stdout}\n'
                '------------------------------------------------------------\n'
            )
            if status != excepted_exit_code:
                raise AssertionError(msg)
            else:
                print(msg)

        if strip_line_prefix:
            # Skip header lines:
            lines = stdout.splitlines()
            found = False
            for pos, line in enumerate(lines, start=1):
                if line.lstrip().startswith(strip_line_prefix):
                    stdout = '\n'.join(lines[pos:])
                    found = True
                    break

            assert found is True, f'Line that starts with {strip_line_prefix=} not found in: {stdout!r}'

            stdout = '\n'.join(line.rstrip() for line in stdout.splitlines())

        return stdout
