"""
    :created: 26.03.2018 by Jens Diemer
    :copyleft: 2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

# https://github.com/jedie/django-tools
from django_tools.exception_plus import print_exc_plus
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer


def test_exception_plus():
    try:
        var = "Test 123"
        raise RuntimeError(var)
    except RuntimeError:
        with StdoutStderrBuffer() as buff:
            print_exc_plus(stop_local_vars=["site-packages"])

        output = buff.get_output()
        print(output)

        assert "RuntimeError: Test 123" in output

        assert "Locals by frame, most recent call first:" in output
        assert ", in test_exception_plus" in output
        assert "var =  'Test 123'" in output
