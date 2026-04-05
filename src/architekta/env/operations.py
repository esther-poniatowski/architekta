"""Pure domain operations for environment management."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from architekta.env.exceptions import InvalidPackagePath, CondaEnvNotFound
from architekta.env.utils import (
    PackageSpec,
    is_base_conda_env,
    is_current_conda_env,
    resolve_package_paths,
)


@dataclass(frozen=True)
class EditableInstallRequest:
    """Explicit configuration for planning editable installs."""

    workspace_root: Path
    site_packages: Path
    package_names: tuple[str, ...] = field(default_factory=tuple)
    use_all: bool = False
    custom_path: Path | None = None
    include_tests: bool = False
    force: bool = False
    active_env: Optional[str] = None
    conda_prefix: Optional[str] = None
    target_env: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "workspace_root", self.workspace_root.expanduser().resolve())
        object.__setattr__(self, "site_packages", self.site_packages.expanduser())
        object.__setattr__(self, "package_names", tuple(self.package_names))


@dataclass(frozen=True)
class InstallPlan:
    """A single editable-install action to execute."""
    package: PackageSpec
    pth_file: Path
    lines: tuple[str, ...]
    skipped: bool = False
    skip_reason: str = ""


@dataclass(frozen=True)
class InstallResult:
    """Result of planning an editable install."""
    plans: tuple[InstallPlan, ...]
    site_packages: Path


def plan_editable_install(request: EditableInstallRequest) -> InstallResult:
    """Plan editable installs without performing I/O.

    Raises
    ------
    CondaEnvNotFound
        If target_env is specified but not the active environment.
    InvalidPackagePath
        If a package path is invalid.
    """
    if request.target_env is not None and not is_current_conda_env(request.target_env, request.active_env):
        raise CondaEnvNotFound(f"Conda environment '{request.target_env}' is not active.")

    if is_base_conda_env(request.conda_prefix):
        raise CondaEnvNotFound("Modifying the base Conda environment is not permitted.")

    specs = resolve_package_paths(
        workspace_root=request.workspace_root,
        package_names=request.package_names,
        use_all=request.use_all,
        custom_path=request.custom_path,
    )

    plans = []
    for spec in specs:
        if not spec.path.exists():
            raise InvalidPackagePath(f"Package path not found: {spec.path}")

        pth_file = request.site_packages / f"{spec.name}.pth"
        lines = [str(spec.path.resolve())]

        if request.include_tests:
            test_path = spec.path.parent / "tests"
            if test_path.exists():
                lines.append(str(test_path.resolve()))

        skipped = False
        skip_reason = ""
        if not request.force and pth_file.exists():
            skipped = True
            skip_reason = f".pth file already exists: {pth_file} (use --force to overwrite)"

        plans.append(
            InstallPlan(
                package=spec,
                pth_file=pth_file,
                lines=tuple(lines),
                skipped=skipped,
                skip_reason=skip_reason,
            )
        )

    return InstallResult(plans=tuple(plans), site_packages=request.site_packages)


def execute_install_plans(result: InstallResult) -> None:
    """Execute planned editable installs by writing .pth files."""
    for plan in result.plans:
        if plan.skip_reason:
            continue
        plan.pth_file.write_text("\n".join(plan.lines))
