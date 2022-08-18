import inspect
import io
from typing import Tuple

from django.core.management import BaseCommand, call_command

from django_tools.unittest_utils.stdout_redirect import DenyStdWrite


class Buffer(io.StringIO):
    def __repr__(self):
        return '<captured_call_command StringIO buffer>'


def captured_call_command(command, **kwargs) -> Tuple[str, str]:
    """
    Call django manage command and return stdout + stderr
    """
    try:
        assert inspect.ismodule(command)
        CommandClass = getattr(command, 'Command')
        assert issubclass(CommandClass, BaseCommand)
    except Exception as err:
        raise AssertionError(f'{command!r} is no Django Management command: {err}')

    command_name = command.__name__
    command_name = command_name.rsplit('.', 1)[-1]

    command_instance = CommandClass()

    capture_stdout = Buffer()
    capture_stderr = Buffer()
    kwargs.update(
        dict(
            stdout=capture_stdout,
            stderr=capture_stderr,
        )
    )
    with DenyStdWrite(name=command_name):
        call_command(command_instance, **kwargs)

    stdout_output = capture_stdout.getvalue()
    stderr_output = capture_stderr.getvalue()
    return stdout_output, stderr_output
