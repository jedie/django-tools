from django.apps import AppConfig


class ModelVersionProtectConfig(AppConfig):
    name = 'django_tools.model_version_protect'
    verbose_name = (
        'Protect overwriting model instance with a older entry'
        ' by auto increment a version number'
    )
