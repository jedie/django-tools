"""
    Dynamic SITE ID unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012-2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

# https://github.com/jedie/django-tools
from django_tools.debug.delay import SessionDelay
from django_tools.middlewares.ThreadLocal import get_current_request


log = logging.getLogger(__name__)


@never_cache
def display_site(request):
    settings_id = settings.SITE_ID
    current_site = Site.objects.get_current()
    current_id = current_site.id

    txt = f"ID from settings: {settings_id!r} - id from get_current(): {current_id!r}"
    log.debug("display_site(): %s", txt)
    return HttpResponse(txt)


class ExampleException(Exception):
    pass


def raise_exception(request, msg=""):
    """
    This view just raises an exception as a way to test middleware exception
    handling.
    """
    raise ExampleException(msg)


def get_current_get_parameters(request):
    """
    Returns a JSON version of request.GET from the current request
    """
    return HttpResponse(json.dumps(get_current_request().GET))


class TemplateDoesNotExists(TemplateView):
    template_name = "/template/does/not/exists.html"


def create_message_normal_response(request, msg):
    messages.info(request, msg)
    return HttpResponse("django_tools_project.django_tools_test_app.views.create_message_normal_response")


def create_message_redirect_response(request, msg):
    messages.info(request, msg)
    return HttpResponseRedirect("/create_message_redirect_response/")


def delay_view(request):
    """
    Used in django_tools_tests.test_debug_delay.SessionDelayTests
    """
    SessionDelay(request, key="delay_view", only_debug=False).load(request, query_string="sec", default=5)

    SessionDelay(request, key="delay_view").sleep()

    return HttpResponse("django_tools_project.django_tools_test_app.views.delay_view")
