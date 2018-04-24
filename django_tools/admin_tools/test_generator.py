
"""
    :created: 24.04.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.model_test_code_generator import ModelTestGenerator


def generate_test_code(modeladmin, request, queryset):
    """
    Django admin action to generate unittest code from model instances.

    To activate globally for all models, put this into one of your admin.py, e.g.:
        admin.site.add_action(generate_test_code)

    Select in admin some model entries and call the action from drop-down menu.
    """
    user = request.user
    if not user.is_superuser:
        messages.error(request, "Only allowed for superusers!")
        return

    model_test_generator = ModelTestGenerator()
    content = model_test_generator.from_queryset(queryset)
    # print(content)

    response = HttpResponse(content, content_type="text/python")

    model_label = modeladmin.model._meta.label
    response['Content-Disposition'] = 'attachment; filename=%s.py' % model_label

    return response


generate_test_code.short_description = _("Generate unittest code")
