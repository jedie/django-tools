"""
    utils around django messages
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    http://docs.djangoproject.com/en/dev/ref/contrib/messages/

    :copyleft: 2010-2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import warnings

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage

from django_tools.middlewares import ThreadLocal
from django_tools.utils.stack_info import get_stack_info


STACK_LIMIT = 6  # Display only the last X stack lines
MAX_FILEPATH_LEN = 50  # Cut filepath in stack info message


class FileLikeMessages:
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


# ------------------------------------------------------------------------------


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
    {% for m in messages %}
    <li{% if m.tags %} class="{{ m.tags }}"{% endif %}{% if m.stack_info %}
        title="click for stack info" onclick="
        alert(
            'Stack info (limit: {{ m.stack_limit }}, url: [{{ m.full_path }}]):\n\n{{ m.stack_info }}'
        );"{% endif %}>
       {{ m }}
    </li>
    {% endfor %}
    </ul>
    """
    _add_stackinfo = settings.DEBUG or getattr(settings, "MESSAGE_DEBUG", False)

    def add(self, *args, **kwargs):
        """ Add stackinfo to the message """
        super().add(*args, **kwargs)

        if self._add_stackinfo:
            # info: self._queued_messages is a normal list, defined in BaseStorage()
            message_list = self._queued_messages
            try:
                last_message = message_list[-1]
            except IndexError:
                return

            last_message.full_path = self.request.get_full_path()
            last_message.stack_limit = STACK_LIMIT

            stack_info = get_stack_info(
                filepath_filter="django_tools",
                stack_limit=STACK_LIMIT,
                max_filepath_len=MAX_FILEPATH_LEN
            )
            stack_info_safe = "\\n".join(
                entry.replace("\n", "\\n").replace("'", "&#x27;")
                for entry in stack_info
            )
            last_message.stack_info = stack_info_safe


# ------------------------------------------------------------------------------


def failsafe_message(msg, level=messages.INFO):
    """
    Display a message to the user.
    Use ThreadLocalMiddleware to get the current request object.
    If no request object is available, create a warning.
    """
    request = ThreadLocal.get_current_request()
    if request:
        # create a normal user message
        try:
            messages.add_message(request, level, msg)
        except Exception as err:
            # e.g.:
            # Without the django.contrib.messages middleware,
            # messages can only be added to authenticated users.
            msg += f" (Error create a message: {err})"
        else:
            return

    # fallback: Create a warning
    warnings.warn(msg)
