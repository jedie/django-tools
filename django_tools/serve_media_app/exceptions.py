import logging

from django.core.exceptions import SuspiciousOperation


logger = logging.getLogger(__name__)


class NoUserToken(SuspiciousOperation):
    def __init__(self, *, user):
        logger.error('Current user "%s" has no token!', user)
