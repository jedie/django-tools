"""

    TODO: Move this!
    from: django_tools/unittest_utils/logging_utils.py
    to..: django_tools/logging_utils.py

    :created: 2015 by Jens Diemer
    :copyleft: 2015-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging


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
        return f"...{pathname[-(self.max_length - 3):]}"

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
            self.external_package_paths = ("/dist-packages/", "/site-packages/")
        else:
            self.external_package_paths = external_package_paths

    def __call__(self, message, category, filename, lineno, args=None, exc_info=None):

        # handle warnings from external packages:
        for path_part in self.external_package_paths:
            if path_part in filename:
                if filename not in self.skipped_filenames:
                    self.skipped_filenames.append(filename)
                    self.logger.warning(f"There are warnings in: {filename}")
                return

        # Create log entry for the warning:
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=logging.WARNING,
            fn=filename,
            lno=lineno,
            msg=f"{category.__name__}:{message}",
            args=args,
            exc_info=exc_info,
        )
        self.logger.handle(record)
