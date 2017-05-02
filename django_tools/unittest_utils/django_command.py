# coding: utf-8

"""
    DjangoCommandMixin
    ~~~~~~~~~~~~~~~~~~

    :copyleft: 2012-2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, print_function

import os
import pprint
import subprocess

import sys


class DjangoCommandMixin(object):
    def subprocess_getstatusoutput(self, cmd, debug=False, **kwargs):
        """
        Return (status, output) of executing cmd in a shell.

        similar to subprocess.getstatusoutput but pass though kwargs
        """

        # Assume that DJANGO_SETTINGS_MODULE not in environment
        # e.g:
        #   manage.py use os.environ.setdefault("DJANGO_SETTINGS_MODULE",...)
        #   so it will ignore the own module path!
        # You can set env by given kwargs, too.
        env=dict(os.environ)
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
            assert os.path.isdir(cwd), "cwd %r doesn't exists!" % cwd
            if debug:
                print("DEBUG: cwd %r, ok" % cwd)

        cmd=" ".join(cmd) # FIXME: Why?!?
        try:
            output = subprocess.check_output(cmd, **subprocess_kwargs)
            status = 0
        except subprocess.CalledProcessError as ex:
            output = ex.output
            status = ex.returncode

        if output[-1:] == '\n':
            output = output[:-1]

        if status != 0 or debug:
            msg = (
                "subprocess exist status == %(status)r\n"
                "Call %(cmd)r with:\n"
                "%(kwargs)s\n"
                "subprocess output:\n"
                "------------------------------------------------------------\n"
                "%(output)s\n"
                "------------------------------------------------------------\n"
            ) % {
                "status": status,
                "cmd": cmd,
                "kwargs": pprint.pformat(subprocess_kwargs),
                "output": output
            }
            if status != 0:
                raise AssertionError(msg)
            else:
                print(msg)

        return output

    def call_manage_py(self, cmd, manage_dir, manage_py="manage.py", assert_executeable=True, **kwargs):
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

        if assert_executeable and not os.access(test_path, os.X_OK):
            msg = (
                "Manage file %r is not executeable!"
            ) % test_path
            raise AssertionError(msg)

        cmd = [sys.executable, "manage.py"] + list(cmd)
        kwargs.update({
            "cwd": manage_dir,
            #"debug": True,
        })
        return self.subprocess_getstatusoutput(cmd, **kwargs)

