import inspect
import io

from cli_base.cli_tools.test_utils.rich_test_utils import BASE_WIDTH, NoColorEnvRich
from click._compat import strip_ansi as strip_ansi_codes
from django.core.management import BaseCommand, call_command

from django_tools.unittest_utils.stdout_redirect import DenyStdWrite


class Buffer(io.StringIO):
    def __repr__(self):
        return '<captured_call_command StringIO buffer>'


def captured_call_command(command, width: int = BASE_WIDTH, strip_ansi: bool = True, **kwargs) -> tuple[str, str]:
    """
    Call django manage command and return stdout + stderr
    """
    with NoColorEnvRich(width=width):
        assert inspect.ismodule(command), f'{command=} is no module'
        CommandClass = command.Command
        assert issubclass(CommandClass, BaseCommand), f'{command=} is no Django Management command'

        command_name = command.__name__
        command_name = command_name.rsplit('.', 1)[-1]

        command_instance = CommandClass()

        capture_stdout = Buffer()
        capture_stderr = Buffer()
        kwargs.update(
            {
                'stdout': capture_stdout,
                'stderr': capture_stderr,
            }
        )
        with DenyStdWrite(name=command_name):
            call_command(command_instance, **kwargs)

        stdout_output = capture_stdout.getvalue()
        stderr_output = capture_stderr.getvalue()

        if strip_ansi:
            stdout_output = strip_ansi_codes(stdout_output)
            stderr_output = strip_ansi_codes(stderr_output)

        return stdout_output, stderr_output
