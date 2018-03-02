# coding: utf-8

from __future__ import unicode_literals, absolute_import


try:
    import celery
except ImportError as err:
    celery = None
    celery_import_error = err

from django.test import override_settings


class task_always_eager(override_settings):
    """
    Decorator that set 'task_always_eager=True' in settings, so that
    all Celery tasks will be executed locally instead of being sent to the queue

    CELERY_ALWAYS_EAGER:
    http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_always_eager
    """
    def __init__(self):
        if celery is None:
            raise ImportError(celery_import_error)

        super(task_always_eager, self).__init__(
            CELERY_ALWAYS_EAGER=True,
            CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        )

        from celery import current_app
        current_app.conf.CELERY_ALWAYS_EAGER = True
        current_app.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
