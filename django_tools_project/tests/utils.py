import shutil
from pathlib import Path
from unittest import TestCase

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.django_command import DjangoCommandMixin


class ForRunnersCommandTestCase(DjangoCommandMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        # installed via setup.py entry points !
        cls.django_tools_bin = shutil.which("django_tools")
        cls.manage_bin = shutil.which("manage")

    def _call_django_tools(self, cmd, **kwargs):
        django_tools_path = Path(self.django_tools_bin)
        return self.call_manage_py(
            cmd=cmd,
            manage_dir=str(django_tools_path.parent),
            manage_py=django_tools_path.name,  # Python 3.5 needs str()
            **kwargs,
        )

    def _call_manage(self, cmd, **kwargs):
        manage_path = Path(self.manage_bin)
        return self.call_manage_py(
            cmd=cmd, manage_dir=str(manage_path.parent), manage_py=manage_path.name, **kwargs  # Python 3.5 needs str()
        )
