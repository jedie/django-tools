class SignalsContextManager:
    def __init__(self, signal, callback):
        self.signal = signal
        self.callback = callback

    def __enter__(self):
        self.signal.connect(self.callback)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.signal.disconnect(self.callback)
