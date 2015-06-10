import io
import sys

from django.utils.six import PY2


class StdoutStderrBuffer():
    """
    redirect stderr and stdout for Py2 and Py3

    contextlib.redirect_stdout is new in Python 3.4!
    and we redirect stderr, too.
    """
    def __init__(self):
        sys.stdout.flush()
        sys.stderr.flush()
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        if PY2:
            self.buffer = io.BytesIO()
        else:
            self.buffer = io.StringIO()


        sys.stdout = sys.stderr = self.buffer

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.old_stdout.flush()
        self.old_stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

    def get_output(self):
        self.old_stdout.flush()
        self.old_stderr.flush()
        output = self.buffer.getvalue()
        if PY2:
            output = output.decode("utf-8")
        return output



