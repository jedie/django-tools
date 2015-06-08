import logging
from logging.handlers import MemoryHandler


class LoggingBuffer():
    def __init__(self, name=None, level=logging.DEBUG, formatter = None):
        self.buffer = []
        self.level=level
        if formatter is None:
            self.formatter = logging.Formatter(logging.BASIC_FORMAT)
        else:
            self.formatter = formatter

        self.log = logging.getLogger(name)
        self.old_handlers = self.log.handlers[:] # .copy()
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

    def get_messages(self):
        return "\n".join([self.formatter.format(record) for record in self.buffer])