from pathlib import Path

from creole.setup_utils import update_rst_readme
from poetry_publish.publish import poetry_publish
from poetry_publish.utils.subprocess_utils import verbose_check_call

import django_tools


PACKAGE_ROOT = Path(django_tools.__file__).parent.parent


def update_readme():
    return update_rst_readme(
        package_root=PACKAGE_ROOT,
        filename='README.creole'
    )


def publish():
    """
        Publish python-creole to PyPi
        Call this via:
            $ poetry run publish
    """
    verbose_check_call('make', 'pytest')  # don't publish if tests fail
    verbose_check_call('make', 'fix-code-style')  # don't publish if code style wrong

    poetry_publish(
        package_root=PACKAGE_ROOT,
        version=django_tools.__version__,
        creole_readme=True  # don't publish if README.rst is not up-to-date
    )
