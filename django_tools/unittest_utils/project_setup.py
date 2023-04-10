import warnings
from pathlib import Path


def check_editor_config(package_root: Path, config_defaults=None) -> None:
    warnings.warn(
        "Use manageprojects.test_utils.project_setup.check_editor_config!",
        DeprecationWarning,
        stacklevel=2,
    )

    from manageprojects.test_utils.project_setup import check_editor_config

    check_editor_config(package_root=package_root, config_defaults=config_defaults)
