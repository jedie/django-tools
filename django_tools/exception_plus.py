import warnings

from bx_py_utils.error_handling import print_exc_plus as print_exc_plus2


def print_exc_plus(exc=None, stop_on_file_path=None, max_chars=None):
    """
    Print the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """
    warnings.warn("Use bx_py_utils.error_handling.print_exc_plus!", DeprecationWarning, stacklevel=2)
    print_exc_plus2(exc=exc, stop_on_file_path=stop_on_file_path, max_chars=max_chars)
