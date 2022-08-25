import logging
import syslog


class SyslogHandler(logging.Handler):
    """
    Replacement for logging.handlers.SysLogHandler()
    Just use syslog.syslog() to emit a log message.
    """

    LEVEL_MAP = {
        logging.CRITICAL: syslog.LOG_EMERG,
        logging.ERROR: syslog.LOG_ERR,
        logging.WARNING: syslog.LOG_WARNING,
        logging.INFO: syslog.LOG_INFO,
        logging.DEBUG: syslog.LOG_DEBUG,
        logging.NOTSET: 'NOTSET',
    }

    def emit(self, record: logging.LogRecord):
        if record.levelno == logging.NOTSET:
            return

        try:
            syslog_priority = self.LEVEL_MAP[record.levelno]
        except KeyError:
            syslog.syslog(
                syslog.LOG_ERR,
                f'Log level {record.levelno!r} ({record.levelname}) is unknown, fallback to WARNING.',
            )
            syslog_priority = syslog.LOG_WARNING

        message = record.getMessage()
        syslog.syslog(syslog_priority, message)
