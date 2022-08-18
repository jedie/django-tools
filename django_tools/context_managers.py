class MassContextManagerBase:
    """
    ContextManager enter and exit more managers ;)
    """

    context_managers = None  # Should be set by child class

    def __enter__(self):
        assert self.context_managers
        for cm in self.context_managers:
            cm.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for cm in self.context_managers:
            cm.__exit__(exc_type, exc_val, exc_tb)
