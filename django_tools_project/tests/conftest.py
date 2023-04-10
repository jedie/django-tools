import os

import pytest


# Avoid django.core.exceptions.SynchronousOnlyOperation:
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', '1')


@pytest.fixture(scope='session')
def browser_context_args(browser_context_args):
    browser_context_args['ignore_https_errors'] = True
    return browser_context_args
