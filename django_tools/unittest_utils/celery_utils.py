"""
    Helper around celery tests

    :created: 04.09.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import time
from pprint import pprint

from celery import current_app
from celery.result import AsyncResult


class WongTestSetup(AssertionError):
    """
    e.g.: Use on_message with a non async backend, see also: https://github.com/celery/celery/issues/5033
    """
    pass


class NotAsyncCall(AssertionError):
    """
    Task call didn't return celery.result.AsyncResult instance.
    e.g.: didn't use "foobar_task.apply_async" as task_func
    """
    pass


def print_celery_report(current_app=None):
    """
    print celery report simmilar to `celery -A proj report` call.
    """
    print("")
    print("_" * 100)
    print("Celery bug report:", flush=True)
    if current_app is None:
        from celery import current_app

    report = current_app.bugreport()
    print(report)

    print("-" * 100, flush=True)


def print_celery_info(current_app=None):
    print("")
    print("_" * 100)
    print("Celery info:", flush=True)

    if current_app is None:
        from celery import current_app

    print("Current app: %r" % current_app)
    print("config:")
    pprint(dict(current_app.conf))

    print("-" * 100, flush=True)


class CallCeleryTask:
    """
    Helper to call a celery task and collection status messages

    examples, see:
        django-tools/django_tools_tests/test_unittest_celery.py
    """

    def __init__(self, *, task_func, func_kwargs=None, hard_timeout=5):
        """
        :param task_func: e.g.: my_task.apply_async
        :param func_kwargs: pass to task_func, e.g.: {countdown=3, "kwargs": {"my_task_kwarg1": "foo"}}
        :param hard_timeout: if != None: Kill complete test process if timeout expires
        """
        if func_kwargs is None:
            func_kwargs = {}

        self.start_task_time = None
        self.task_duration = None

        current_backend = current_app.backend
        self.backend_is_async = current_backend.is_async

        if self.backend_is_async:
            # e.g.: RPC or redis backens are async and support on_message callback
            # see: https://github.com/celery/celery/issues/5033
            self.raw_messages = []
            self._on_message_callback = self._save_on_message
        else:
            self.raw_messages = None
            self._on_message_callback = None

        print("Create Task with %r kwargs:%r" % (task_func, func_kwargs))
        self.create_task_time = time.time()
        self.async_result = task_func(**func_kwargs)

        if not isinstance(self.async_result, AsyncResult):
            msg = (
                "Task %r not returned a AsyncResult instance"
                " (not called via e.g.: .apply_async() ?!?)"
                " has returned: %r"
            ) % (task_func, self.async_result)
            raise NotAsyncCall(msg)

        if hard_timeout:
            # timeout in celery doesn't work in some cases:
            #   https://github.com/celery/celery/issues/5034
            #
            # This works:
            self.async_result.wait(timeout=hard_timeout, propagate=True)

        self.create_task_duration = time.time() - self.create_task_time
        print("Create Task duration: %.3f sec." % self.create_task_duration)

    def get_result(self):
        """
        :return: celery.result.AsyncResult instance
        """
        print("Wait until task is ready, and save its result")
        self.start_task_time = time.time()
        try:
            result = self.async_result.get(
                # timeout=self.max_task_duration, <<< Will not work with RPC backend, see: https://github.com/celery/celery/issues/5034
                on_message=self._on_message_callback,
                propagate=False
            )
        except Exception as err:
            self.task_duration = time.time() - self.start_task_time
            raise AssertionError("Error get task results: %s" % err)

        self.task_duration = time.time() - self.start_task_time
        print("Task result after: %.3f sec.: %r" % (self.task_duration, result))
        return result

    def _save_on_message(self, message_dict):
        """
        on_message handler function, see:
        http://docs.celeryproject.org/en/latest/userguide/calling.html#on-message
        """
        # print("on_message callback:", end=" ")
        # pprint(message_dict)
        self.raw_messages.append(message_dict)

    def get_messages(self):
        """
        :return: List of created task state messages in "short" format
        """
        if not self.backend_is_async:
            raise WongTestSetup("Only async backends (e.g.: RPC, redit) support on_message callback!")

        print("Task Messages:", end=" ")
        assert self.start_task_time is not None, "You have to call get_result() first!"
        messages = ["%s: %s" % (msg["status"], msg["result"]) for msg in self.raw_messages]
        pprint(messages)
        return messages


def assert_celery_async_call(
    *,
    task_func,
    func_kwargs=None,
    hard_timeout=None,
    result=None,
    messages=None,
    max_task_duration=None,
    max_create_task_duration=None
):
    """
    Run celery tasks and assert results.

    examples, see:
        django-tools/django_tools_tests/test_unittest_celery.py

    :param task_func: pass to CallCeleryTask
    :param func_kwargs: pass to CallCeleryTask
    :param hard_timeout: pass to CallCeleryTask

    :param result: if not None: assert the task result
    :param messages: if not None: assert on_message output
    :param max_task_duration: if not None: assert the task duration
    :param max_create_task_duration: if not None: assert the task create duration
    """
    t = CallCeleryTask( # if celery is in eager mode, then the AssertionError will happen here!
        task_func=task_func,
        func_kwargs=func_kwargs,
        hard_timeout=hard_timeout,
    )

    task_result = t.get_result()

    if result is not None:
        if isinstance(result, Exception):
            assert isinstance(task_result, result.__class__), "%r != %r" % (task_result, result)
            assert str(task_result) == str(result), "%s != %s" % (task_result, result)
        else:
            assert task_result == result, "%r != %r" % (task_result, result)

    if messages is not None:
        # Note: Only async backends (e.g.: RPC, redit) support on_message callback!
        task_messages = t.get_messages()
        assert task_messages == messages, "%r != %r" % (task_messages, messages)

    if max_task_duration:
        assert t.task_duration <= max_task_duration, "%s is greater than %s" % (t.task_duration, max_task_duration)

    if max_create_task_duration:
        assert t.create_task_duration <= max_create_task_duration, "%s is greater than %s" % (
            t.create_task_duration, max_create_task_duration
        )
