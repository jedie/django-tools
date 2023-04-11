import logging
import syslog
from unittest import TestCase, mock

from django_tools.context_managers import MassContextManagerBase
from django_tools.log_utils import syslog_handler
from django_tools.log_utils.syslog_handler import SyslogHandler


class SyslogMock:
    def __init__(self):
        self._messages = []
        self._level_map = {
            syslog.LOG_EMERG: 'LOG_EMERG',
            syslog.LOG_ERR: 'LOG_ERR',
            syslog.LOG_WARNING: 'LOG_WARNING',
            syslog.LOG_INFO: 'LOG_INFO',
            syslog.LOG_DEBUG: 'LOG_DEBUG',
        }

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return getattr(syslog, item)

    def syslog(self, priority, message):
        priority_name = self._level_map[priority]
        self._messages.append((priority_name, message))


class SyslogHandlerMock(MassContextManagerBase):
    def __init__(self):
        self.syslog_mock = SyslogMock()

    def __enter__(self):
        self.context_managers = [mock.patch.object(syslog_handler, 'syslog', self.syslog_mock)]
        return super().__enter__()

    def get_messages(self):
        return self.syslog_mock._messages


class SyslogHandlerTestCase(TestCase):
    def setUp(self) -> None:
        logger = logging.getLogger(__file__)
        handler = SyslogHandler()
        handler.setLevel(1)
        logger.addHandler(handler)
        logger.setLevel(1)
        self.logger = logger

    def tearDown(self) -> None:
        self.logger.handlers.clear()

    def test_syslog_handler(self):
        with SyslogHandlerMock() as m:
            self.logger.debug('Test DEBUG message')
            self.logger.info('Test INFO message')
            self.logger.warning('Test WARNING message')
            self.logger.error('Test ERROR message')
            self.logger.critical('Test CRITICAL message')
            self.logger.exception('Test a exception log message')
            self.logger.log(level=1, msg='Test level=1 log message')
            self.logger.log(level=99, msg='Test level=99 log message')
            self.logger.log(level=logging.NOTSET, msg='Test NOTSET message')

        messages = m.get_messages()
        self.assertEqual(
            messages,
            [
                ('LOG_DEBUG', 'Test DEBUG message'),
                ('LOG_INFO', 'Test INFO message'),
                ('LOG_WARNING', 'Test WARNING message'),
                ('LOG_ERR', 'Test ERROR message'),
                ('LOG_EMERG', 'Test CRITICAL message'),
                ('LOG_ERR', 'Test a exception log message'),
                ('LOG_ERR', 'Log level 1 (Level 1) is unknown, fallback to WARNING.'),
                ('LOG_WARNING', 'Test level=1 log message'),
                ('LOG_ERR', 'Log level 99 (Level 99) is unknown, fallback to WARNING.'),
                ('LOG_WARNING', 'Test level=99 log message'),
            ],
        )
