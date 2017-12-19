from django.contrib import admin

from django_tools_test_project.django_tools_test_app.models import PermissionTestModel


@admin.register(PermissionTestModel)
class PermissionTestModelAdmin(admin.ModelAdmin):
    pass
