from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = 'django_tools'
    verbose_name = 'django-tools'

    def ready(self):
        import django_tools.checks  # noqa
