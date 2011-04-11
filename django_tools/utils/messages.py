# coding:utf-8

"""
    utils around django messages
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    http://docs.djangoproject.com/en/dev/ref/contrib/messages/
    
    :copyleft: 2010-2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import inspect
import warnings

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage

from django_tools.middlewares import ThreadLocal


STACK_LIMIT = 6 # Display only the last X stack lines
MAX_FILEPATH_LEN = 50 # Cut filepath in stack info message


class FileLikeMessages(object):
    """
    Simple layer around messages, to get a file-like object.
    
    usage e.g.:
    
    page_msg = FileLikeMessages(request, messages.INFO)
    page_msg.write("This is it!")
    page_msg("Call works's, too.")
    """
    def __init__(self, request, msg_level):
        self.request = request
        self.msg_level = msg_level

    def write(self, txt):
        messages.add_message(self.request, self.msg_level, txt)

    __call__ = write


#------------------------------------------------------------------------------


class StackInfoStorage(FallbackStorage):
    """
    Message storage like LegacyFallbackStorage, except, every message
    would have a stack info, witch is helpful, for debugging.
    
    Stack info would only be added, if...
        ...settings.DEBUG == True
    or
        ...settings.MESSAGE_DEBUG == True
    
    Put this into your settings:
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    MESSAGE_STORAGE = "django_tools.utils.messages.StackInfoStorage"
    
    Template e.g.:
    ~~~~~~~~~~~~~~
    <ul class="messages">
    {% for message in messages %}
    <li{% if message.tags %} class="{{ message.tags }}"{% endif %}{% if message.stack_info %} title="click for stack info" onclick="alert('Stack info (limit: {{ message.stack_limit }}, url: [{{ message.full_path }}]):\n\n{{ message.stack_info }}');"{% endif %}>
       {{ message }}
    </li>
    {% endfor %}
    </ul>
    """
    _add_stackinfo = settings.DEBUG or getattr(settings, "MESSAGE_DEBUG", False)

    def add(self, *args, **kwargs):
        """ Add stackinfo to the message """
        super(StackInfoStorage, self).add(*args, **kwargs)

        if self._add_stackinfo:
            # info: self._queued_messages is a normal list, defined in BaseStorage()
            message_list = self._queued_messages
            try:
                last_message = message_list[-1]
            except IndexError:
                pass
            else:
                last_message.full_path = self.request.get_full_path()
                last_message.stack_limit = STACK_LIMIT
                last_message.stack_info = self._get_stack_info()

    def _get_stack_info(self):
        """
        return stack_info: Where from the announcement comes?
        """
        stack_list = inspect.stack()
        stack_list.reverse()

        # go forward in the stack, till outside of this file.
        for no, stack_line in enumerate(stack_list):
            filepath = stack_line[1]
            if filepath == __file__:
                break

        # Display only the last entries, till outside of this file
        stack_list = stack_list[:no]
        stack_list = stack_list[-STACK_LIMIT:]

        stack_info = []
        for stack_line in stack_list:
            filename = stack_line[1]
            if len(filename) >= MAX_FILEPATH_LEN:
                filename = "...%s" % filename[-MAX_FILEPATH_LEN:]

            lineno = stack_line[2]
            func_name = stack_line[3]

            stack_info.append("%s %4s %s" % (filename, lineno, func_name))

        return "\\n\\n".join(stack_info)


#------------------------------------------------------------------------------


def failsafe_message(msg, level=messages.INFO):
    """
    Display a message to the user.
    Use ThreadLocalMiddleware to get the current request object.
    If no request object is available, create a warning.
    """
    request = ThreadLocal.get_current_request()
    if request:
        # create a normal user message
        messages.add_message(request, level, msg)
    else:
        # fallback: Create a warning
        warnings.warn(msg)
