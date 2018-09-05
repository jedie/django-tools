"""
    Test the helper around celery tests utilities

    :created: 04.09.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import pytest

from django_tools_test_project.django_tools_test_app.tasks import sleep_task, test_task

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_celery_not_eager
from django_tools.unittest_utils.celery_utils import WongTestSetup, assert_celery_async_call, print_celery_report
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer


@pytest.mark.celery
def test_print_celery_report(celery_worker):
    with StdoutStderrBuffer() as buffer:
        print_celery_report()
    output = buffer.get_output()
    print(output)

    assert "software -> celery" in output
    assert "settings -> transport:memory results:cache+memory:///" in output

    assert "broker_url: 'memory://localhost//'" in output
    assert "result_backend: 'cache+memory:///'" in output

    assert "django_tools_test_project.django_tools_test_app.tasks" in output


@pytest.mark.celery(result_backend="cache+memory:///", broker_url="memory://")
def test_no_message_support(celery_worker):
    assert_celery_async_call(
        task_func=test_task.apply_async,
        result="return value",
        messages=None,  # no on_message support
        max_task_duration=2,
        max_create_task_duration=0.1,
    )


@pytest.mark.celery(result_backend="rpc", broker_url="memory://")
def test_test_task(celery_worker):
    assert_celery_async_call(
        task_func=test_task.apply_async,
        result="return value",
        messages=["FOO: {'bar': 1}", "FOO: {'bar': 2}", 'SUCCESS: return value'],
        max_task_duration=2,
        max_create_task_duration=0.1,
    )


@pytest.mark.celery(result_backend="rpc", broker_url="memory://")
def test_sleep_task_no_kwargs(celery_worker):
    assert_celery_not_eager()

    assert_celery_async_call(
        task_func=sleep_task.apply_async,
        # func_kwargs={"sleep_time": 0.3},
        result="I have wait 0 sec, ok.",
        messages=["START: {'sleep_time': 0}", "FINISH: {'sleep_time': 0}", 'SUCCESS: I have wait 0 sec, ok.'],
        max_task_duration=2,
        max_create_task_duration=0.1,
    )


@pytest.mark.celery(result_backend="rpc", broker_url="memory://")
def test_sleep_task_with_kwargs(celery_worker):
    assert_celery_async_call(
        task_func=sleep_task.apply_async,
        func_kwargs={"kwargs": {
            "sleep_time": 0.1
        }},
        result="I have wait 0.1 sec, ok.",
        messages=["START: {'sleep_time': 0.1}", "FINISH: {'sleep_time': 0.1}", 'SUCCESS: I have wait 0.1 sec, ok.'],
        max_task_duration=3,
        max_create_task_duration=0.1,
    )


@pytest.mark.celery(result_backend="rpc", broker_url="memory://")
def test_sleep_task_raise_error(celery_worker):
    assert_celery_async_call(
        task_func=sleep_task.apply_async,
        func_kwargs={"kwargs": {
            "sleep_time": "not-a-number!"
        }},
        result=AssertionError("'not-a-number!' is not a number!"),
        messages=["START: {'sleep_time': 'not-a-number!'}", "FAILURE: 'not-a-number!' is not a number!"],
        max_task_duration=3,
        max_create_task_duration=0.1,
    )
