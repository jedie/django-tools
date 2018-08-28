from django.test.utils import TestContextDecorator

try:
    import celery
except ImportError as err:
    celery = None
    celery_import_error = err


class task_always_eager(TestContextDecorator):
    """
    Decorator that set 'task_always_eager=True' and 'task-eager-propagates=True' in settings, so that
    all Celery tasks will be executed locally instead of being sent to the queue

    See also:
        http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-always-eager
        http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates

    See tests here:
        django_tools_tests.test_unittest_utils.TestCeleryDecoratorMethodUsage
        django_tools_tests.test_unittest_utils.TestCeleryDecoratorClassUsage
    """
    def __init__(self):
        if celery is None:
            raise ImportError("Celery is needed to running tests! Origin error: %s" % celery_import_error)
        super().__init__()

    def enable(self):
        from celery import current_app
        self._old_task_always_eager = current_app.conf.task_always_eager
        self._old_task_eager_propagates = current_app.conf.task_eager_propagates

        current_app.conf.task_always_eager = True
        current_app.conf.task_eager_propagates = True

    def disable(self):
        from celery import current_app
        current_app.conf.task_always_eager = self._old_task_always_eager
        current_app.conf.task_eager_propagates = self._old_task_eager_propagates
