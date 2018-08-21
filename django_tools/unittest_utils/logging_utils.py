"""
    :created: 2015 by Jens Diemer
    :copyleft: 2015-2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
from logging.handlers import MemoryHandler


class LoggingBuffer:

    def __init__(self, name=None, level=logging.DEBUG, formatter=None):
        """
        To get the logger name, execute this in `./manage.py shell` e.g.:

        import logging;print("\n".join(sorted(logging.Logger.manager.loggerDict.keys())))
        """
        self.buffer = []
        self.level = level
        if formatter is None:
            self.formatter = logging.Formatter(logging.BASIC_FORMAT)
        else:
            self.formatter = formatter

        self.log = logging.getLogger(name)
        self.old_handlers = self.log.handlers[:]  # .copy()
        self.old_level = self.log.level
        self.log.setLevel(level)
        self.log.handlers = [MemoryHandler(capacity=0, flushLevel=level, target=self)]

    def handle(self, record):
        self.buffer.append(record)

    def clear(self):
        self.buffer = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.log.handlers = self.old_handlers
        self.log.level = self.old_level

    def get_message_list(self):
        return [self.formatter.format(record) for record in self.buffer]

    def get_messages(self):
        return "\n".join(self.get_message_list())

    def assert_messages(self, reference):
        messages = self.get_message_list()
        assert messages == reference, "%r != %r" % (messages, reference)


class CutPathnameLogRecordFactory:
    """
    Adds 'cut_path' attribute on log record. So '%(cut_path)s' can be used in log formatter.

    Add this to you settings.py, e.g.:

        import logging
        from django_tools.unittest_utils.logging_utils import CutPathnameLogRecordFactory

        logging.setLogRecordFactory(CutPathnameLogRecordFactory(max_length=50))

        LOGGING = {
            # ...
            'formatters': {
                'verbose': {
                    'format': '%(levelname)8s %(cut_path)s:%(lineno)-3s %(message)s'
                },
            },
            # ...
        }
    """

    def __init__(self, max_length=40):
        self.max_length = max_length
        self.origin_factory = logging.getLogRecordFactory()

    def cut_path(self, pathname):
        if len(pathname) <= self.max_length:
            return pathname
        return "...%s" % pathname[-(self.max_length - 3):]

    def __call__(self, *args, **kwargs):
        record = self.origin_factory(*args, **kwargs)
        record.cut_path = self.cut_path(record.pathname)
        return record


class FilterAndLogWarnings:
    """
    Filter warnings and pipe them to logging system
    Warnings of external packages are displayed only once and only the file path.

    Activate warnings, e.g.:
        export PYTHONWARNINGS=all

    Add this to you settings.py, e.g.:

        import warnings
        import logging
        from django_tools.unittest_utils.logging_utils import FilterAndLogWarnings

        warnings.showwarning = FilterAndLogWarnings()
    """
    skipped_filenames = []

    def __init__(self, logger_name=None, external_package_paths=None):
        if logger_name is None:
            logger_name = __name__
        self.logger = logging.getLogger(logger_name)

        if external_package_paths is None:
            self.external_package_paths = (
                "/dist-packages/",
                "/site-packages/",
            )
        else:
            self.external_package_paths = external_package_paths

    def __call__(self, message, category, filename, lineno, args=None, exc_info=None):

        # handle warnings from external packages:
        for path_part in self.external_package_paths:
            if path_part in filename:
                if filename not in self.skipped_filenames:
                    self.skipped_filenames.append(filename)
                    self.logger.warning("There are warnings in: %s" % filename)
                return

        # Create log entry for the warning:
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=logging.WARNING,
            fn=filename,
            lno=lineno,
            msg="%s:%s" % (category.__name__, message),
            args=args,
            exc_info=exc_info,
        )
        self.logger.handle(record)
