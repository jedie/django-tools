"""Test project for django-tools."""

from celery import Celery

celery_app = Celery('django_tools_test_project')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

__all__ = ['celery_app']
