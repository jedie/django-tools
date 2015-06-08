import shutil
import tempfile


class TempDir():
    def __init__(self, prefix=""):
        self.tempfolder = tempfile.mkdtemp(prefix=prefix)

    def __enter__(self):
        return self.tempfolder

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.tempfolder)