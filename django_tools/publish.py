from pathlib import Path

from poetry_publish.publish import poetry_publish
from poetry_publish.utils.subprocess_utils import verbose_check_call

import django_tools


PACKAGE_ROOT = Path(django_tools.__file__).parent.parent


def publish():
    """
        Publish python-creole to PyPi
        Call this via:
            $ poetry run publish
    """
    verbose_check_call('make', 'pytest')  # don't publish if tests fail

    poetry_publish(package_root=PACKAGE_ROOT, version=django_tools.__version__, creole_readme=False)
