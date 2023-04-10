import functools
import tempfile
from pathlib import Path

from django.test import override_settings


class TempMediaRoot:
    """
    Context Manager / Decorator to set a temporary MEDIA_ROOT
    """

    def __enter__(self) -> Path:
        self.temp_dir_cm = tempfile.TemporaryDirectory()
        self.temp_dir = self.temp_dir_cm.__enter__()
        self.override_cm = override_settings(MEDIA_ROOT=self.temp_dir)
        self.override_cm.__enter__()
        return Path(self.temp_dir)

    def __exit__(self, exc_type, exc_value, traceback):
        self.temp_dir_cm.__exit__(exc_type, exc_value, traceback)
        self.override_cm.__exit__(exc_type, exc_value, traceback)
        if exc_type:
            return False

    def __call__(self, func):
        """
        Use this Context Manager a Decorator, too
        """

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapped_func
