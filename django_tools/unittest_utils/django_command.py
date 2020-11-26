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
from shlex import quote


class DjangoCommandMixin:
    def subprocess_getstatusoutput(self, cmd, debug=False, excepted_exit_code=0, **kwargs):
        """
        Return (status, output) of executing cmd in a shell.

        similar to subprocess.getstatusoutput but pass though kwargs
        """
        assert isinstance(cmd, (list, tuple))

        # Assume that DJANGO_SETTINGS_MODULE not in environment
        # e.g:
        #   manage.py use os.environ.setdefault("DJANGO_SETTINGS_MODULE",...)
        #   so it will ignore the own module path!
        # You can set env by given kwargs, too.
        env = dict(os.environ)
        if "DJANGO_SETTINGS_MODULE" in env:
            del(env["DJANGO_SETTINGS_MODULE"])

        subprocess_kwargs = {
            "env": env,
            "shell": True,
            "universal_newlines": True,
            "stderr": subprocess.STDOUT,
        }
        subprocess_kwargs.update(kwargs)
        if "cwd" in subprocess_kwargs:
            cwd = subprocess_kwargs["cwd"]
            assert os.path.isdir(cwd), f"cwd {cwd!r} doesn't exists!"
            if debug:
                print(f"DEBUG: cwd {cwd!r}, ok")

        cmd = ' '.join(quote(arg) for arg in cmd)
        try:
            output = subprocess.check_output(cmd, **subprocess_kwargs)
            status = 0
        except subprocess.CalledProcessError as ex:
            output = ex.output
            status = ex.returncode

        output = output.rstrip('\n\x1b[0m')

        if status != excepted_exit_code or debug:
            msg = (
                "subprocess exist status == %(status)r (excepted: %(excepted_exit_code)r)\n"
                "Call %(cmd)r with:\n"
                "%(kwargs)s\n"
                "subprocess output:\n"
                "------------------------------------------------------------\n"
                "%(output)s\n"
                "------------------------------------------------------------\n"
            ) % {
                "status": status,
                "excepted_exit_code": excepted_exit_code,
                "cmd": cmd,
                "kwargs": pprint.pformat(subprocess_kwargs),
                "output": output
            }
            if status != excepted_exit_code:
                raise AssertionError(msg)
            else:
                print(msg)

        return output

    def call_manage_py(self, cmd, manage_dir, manage_py="manage.py", assert_executable=True, **kwargs):
        """
        call manage.py from given >manage_dir<
        """
        test_path = os.path.join(manage_dir, manage_py)
        if not os.path.isfile(test_path):
            msg = (
                "File doesn't exists: %r"
                " (given <manage_dir> path wrong?!?)"
            ) % manage_dir
            raise AssertionError(msg)

        if assert_executable and not os.access(test_path, os.X_OK):
            msg = (
                "Manage file %r is not executable!"
            ) % test_path
            raise AssertionError(msg)

        cmd = [sys.executable, manage_py] + list(cmd)
        kwargs.update({
            "cwd": manage_dir,
            # "debug": True,
        })
        return self.subprocess_getstatusoutput(cmd, **kwargs)
