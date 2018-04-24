from django.contrib import admin

from django_tools_test_project.django_tools_test_app.models import PermissionTestModel

# https://github.com/jedie/django-tools
from django_tools.admin_tools.test_generator import generate_test_code


@admin.register(PermissionTestModel)
class PermissionTestModelAdmin(admin.ModelAdmin):
    pass


# Activate globally for all models:
admin.site.add_action(generate_test_code)
