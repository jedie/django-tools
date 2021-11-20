from django.contrib import admin

# https://github.com/jedie/django-tools
from django_tools.admin_tools.test_generator import generate_test_code
from django_tools_test_project.django_tools_test_app.models import (
    OverwriteFileSystemStorageModel,
    PermissionTestModel,
    VersioningTestModel,
)


@admin.register(PermissionTestModel)
class PermissionTestModelAdmin(admin.ModelAdmin):
    pass


# Activate globally for all models:
admin.site.add_action(generate_test_code)


@admin.register(OverwriteFileSystemStorageModel)
class OverwriteFileSystemStorageModelAdmin(admin.ModelAdmin):
    pass


@admin.register(VersioningTestModel)
class VersioningTestModelModelAdmin(admin.ModelAdmin):
    fields = (
        ('id', 'version'),
        'user',
        'name'
    )
    readonly_fields = ('id',)
