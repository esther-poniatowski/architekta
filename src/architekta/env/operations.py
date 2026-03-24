"""Pure domain operations for environment management."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List

from architekta.env.exceptions import InvalidPackagePath, CondaEnvNotFound
from architekta.env.utils import PackageSpec, get_site_packages, resolve_package_paths


@dataclass(frozen=True)
class InstallPlan:
    """A single editable-install action to execute."""
    package: PackageSpec
    pth_file: Path
    lines: list[str]
    skipped: bool = False
    skip_reason: str = ""


@dataclass(frozen=True)
class InstallResult:
    """Result of planning an editable install."""
    plans: list[InstallPlan]
    site_packages: Path


def plan_editable_install(
    packages: Optional[List[str]],
    use_all: bool,
    custom_path: Optional[Path],
    include_tests: bool,
    force: bool,
    active_env: Optional[str],
    conda_prefix: Optional[str],
    target_env: Optional[str],
) -> InstallResult:
    """Plan editable installs without performing I/O.

    Raises
    ------
    CondaEnvNotFound
        If target_env is specified but not the active environment.
    InvalidPackagePath
        If a package path is invalid.
    """
    from architekta.env.utils import is_current_conda_env, is_base_conda_env

    if target_env is not None and not is_current_conda_env(target_env, active_env):
        raise CondaEnvNotFound(f"Conda environment '{target_env}' is not active.")

    if is_base_conda_env(conda_prefix):
        raise CondaEnvNotFound("Modifying the base Conda environment is not permitted.")

    specs = resolve_package_paths(packages, use_all, custom_path)
    site_pkgs = get_site_packages()

    plans = []
    for spec in specs:
        if not spec.path.exists():
            raise InvalidPackagePath(f"Package path not found: {spec.path}")

        pth_file = site_pkgs / f"{spec.name}.pth"
        lines = [str(spec.path.resolve())]

        if include_tests:
            test_path = spec.path.parent / "tests"
            if test_path.exists():
                lines.append(str(test_path.resolve()))

        skipped = False
        skip_reason = ""
        if not force and pth_file.exists():
            skipped = True
            skip_reason = f".pth file already exists: {pth_file} (use --force to overwrite)"

        plans.append(InstallPlan(
            package=spec,
            pth_file=pth_file,
            lines=lines,
            skipped=skipped,
            skip_reason=skip_reason,
        ))

    return InstallResult(plans=plans, site_packages=site_pkgs)
