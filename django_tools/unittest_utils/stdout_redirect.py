import io
import sys

from django.utils.encoding import smart_text

# origin_stderr = sys.stderr

class StringBuffer(io.StringIO):
    def write(self, data):
        # origin_stderr.write("\nwrite to StringBuffer:\n%s\n\n" % repr(data))
        data = smart_text(data)
        super(StringBuffer, self).write(data)


class StdoutStderrBuffer():
    """
    redirect stderr and stdout for Py2 and Py3

    contextlib.redirect_stdout is new in Python 3.4!
    and we redirect stderr, too.

    We use django.utils.encoding.smart_text in StringBuffer()
    So output of bytes will only work, if there are encoded in UTF-8!

    e.g:

        with StdoutStderrBuffer() as buffer:
            print("foo")

        output = buffer.get_output()
    """
    def __init__(self):
        sys.stdout.flush()
        sys.stderr.flush()
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr

        self.buffer = StringBuffer()

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
        return output



