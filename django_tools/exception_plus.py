"""
    Code based on:
        https://github.com/jedie/python-code-snippets/blob/master/CodeSnippets/traceback_plus.py

    :copyleft: 2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys
import traceback


MAX_CHARS = 256

DEFAULT_STOP_LOCAL_VARS = ("django/core/management/base.py", "django/core/handlers/exception.py", "/wsgiref")


def print_exc_plus(stop_local_vars=None):
    """
    Print the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """
    tb = sys.exc_info()[2]
    while True:
        if not tb.tb_next:
            break
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back

    txt = traceback.format_exc()
    txt_lines = txt.splitlines()
    first_line = txt_lines.pop(0)
    last_line = txt_lines.pop(-1)
    print(first_line)
    for line in txt_lines:
        if line.strip().startswith("File"):
            print(line)
        else:
            print(line)
    print(last_line)

    print_local_vars = True

    if stop_local_vars is None:
        stop_local_vars = DEFAULT_STOP_LOCAL_VARS

    print(" -" * 50)
    print("Locals by frame, most recent call first:")
    for frame in stack:
        file_path = frame.f_code.co_filename
        msg = f'File "{file_path}", line {frame.f_lineno:d}, in {frame.f_code.co_name}'
        print(f"\n *** {msg}", end="", flush=True)

        if stop_local_vars is not None and print_local_vars:
            for path_part in stop_local_vars:
                if path_part in file_path:
                    print_local_vars = False
                    break

        if print_local_vars:
            print()
            for key, value in list(frame.f_locals.items()):
                print("%30s = " % key, end=" ")
                # We have to be careful not to cause a new error in our error
                # printer! Calling str() on an unknown object could cause an
                # error we don't want.
                if isinstance(value, int):
                    value = f"${value:x} (decimal: {value:d})"
                else:
                    value = repr(value)

                if len(value) > MAX_CHARS:
                    value = f"{value[:MAX_CHARS]}..."

                try:
                    print(value)
                except BaseException:
                    print("<ERROR WHILE PRINTING VALUE>")

    print()
    print("=" * 100)
