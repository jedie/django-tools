import inspect
from pathlib import Path


STACK_LIMIT = 6  # Display only the last X stack lines


def format_list(extracted_list):
    """
    Format a list of traceback entry tuples.
    """
    list = []
    cwd = Path.cwd()
    for _, filename, lineno, func_name, line, _ in extracted_list:
        filename = Path(filename)
        try:
            filename = filename.relative_to(cwd)
        except ValueError:
            pass
        code = "".join(line).strip()
        item = ('File "%s", line %d, in %s\n' '  %s') % (filename, lineno, func_name, code)
        list.append(item)
    return list


def get_stack_info(filepath_filter):
    """
    return stack_info: Where from the announcement comes?
    """
    before = True  # before we visit filepath_filter
    after = False  # after we left filepath_filter

    stack_list = []
    for frame in reversed(inspect.stack()):
        filepath = frame[1]

        if before and filepath_filter not in filepath:
            before = False
            continue

        if not after and filepath_filter in filepath:
            after = True

        if after:
            stack_list.append(frame)

    stack_info = format_list(stack_list)
    return stack_info
