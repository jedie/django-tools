#!/usr/bin/env python
# coding: utf-8

"""
    stack information
    ~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import inspect


STACK_LIMIT = 6 # Display only the last X stack lines
MAX_FILEPATH_LEN = 50 # Cut filepath in stack info message


def format_list(extracted_list):
    """
    Format a list of traceback entry tuples.
    """
    list = []
    for _, filename, lineno, func_name, line, _  in extracted_list:
        code = "".join(line).strip()
        item = (
            'File "%s", line %d, in %s\n'
            '  %s\n'
        ) % (filename, lineno, func_name, code)
        list.append(item)
    return list


def get_stack_info(filepath_filter, stack_limit=STACK_LIMIT, max_filepath_len=MAX_FILEPATH_LEN):
    """
    return stack_info: Where from the announcement comes?
    """
    stack_list = inspect.stack()
    stack_list.reverse()

    # go forward in the stack, till outside of this file.
    for no, stack_line in enumerate(stack_list):
        filepath = stack_line[1]
        if filepath_filter in filepath:
            break

    # Display only the last entries, till outside of this file
    stack_list = stack_list[:no]
    stack_list = stack_list[-stack_limit:]

    stack_info = format_list(stack_list)
    return stack_info
