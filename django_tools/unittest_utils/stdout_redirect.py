import io
from contextlib import redirect_stderr, redirect_stdout

from django_tools.context_managers import MassContextManagerBase


class StdoutStderrBuffer(MassContextManagerBase):
    """
    redirect stderr and stdout

    e.g:

        with StdoutStderrBuffer() as buffer:
            print("foo")

        output = buffer.get_output()
    """

    def __init__(self):
        self.buffer = io.StringIO()
        self.context_managers = [
            redirect_stdout(self.buffer),
            redirect_stderr(self.buffer),
        ]

    def get_output(self):
        output = self.buffer.getvalue()
        return output


class DenyStdWriteHandler:
    def __init__(self, name, std_type):
        self.name = name
        self.std_type = std_type

    def write(self, out, *args, **kwargs):
        raise AssertionError(f'{self.name} writes to std{self.std_type}:\n{out}')


class DenyStdWrite(MassContextManagerBase):
    """
    ContextManager that raise an AssertionError on std(out|err).write calls.
    """

    def __init__(self, name):
        self.context_managers = [
            redirect_stdout(DenyStdWriteHandler(name=name, std_type='out')),
            redirect_stderr(DenyStdWriteHandler(name=name, std_type='err')),
        ]
