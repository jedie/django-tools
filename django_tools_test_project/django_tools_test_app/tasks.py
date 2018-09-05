"""
    Example celery task for tests

    :created: 04.09.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import time

from celery import shared_task

log = logging.getLogger(__name__)


@shared_task(bind=True)
def sleep_task(self, sleep_time=0):
    """
    Used in django_tools_tests.test_unittest_celery.TestCelerySetup
    """
    log.warning("Wait %s sec...", sleep_time)
    self.update_state(state="START", meta={"sleep_time": sleep_time})
    assert isinstance(sleep_time, (int, float)), "%r is not a number!" % sleep_time
    time.sleep(sleep_time)
    self.update_state(state="FINISH", meta={"sleep_time": sleep_time})
    return "I have wait %s sec, ok." % sleep_time


@shared_task(bind=True)
def on_message_test_task(self):
    self.update_state(state="FOO", meta={"bar": 1})
    self.update_state(state="FOO", meta={"bar": 2})
    return "return value"
