"""Utilities for explicit editable-install environment planning."""

import sysconfig
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from architekta.env.exceptions import InvalidPackagePath


@dataclass(frozen=True)
class PackageSpec:
    """A resolved package with its name and path."""
    name: str
    path: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", self.path.expanduser())


def get_site_packages() -> Path:
    path = sysconfig.get_paths()["purelib"]
    return Path(path)


def is_current_conda_env(name: str, active_env: Optional[str]) -> bool:
    return active_env == name


def is_base_conda_env(conda_prefix: Optional[str]) -> bool:
    return bool(conda_prefix and Path(conda_prefix).name == "base")


def resolve_package_paths(
    workspace_root: Path,
    package_names: tuple[str, ...],
    use_all: bool,
    custom_path: Optional[Path],
) -> tuple[PackageSpec, ...]:
    src_root = workspace_root / "src"

    if custom_path is not None:
        custom_path = custom_path if custom_path.is_absolute() else workspace_root / custom_path
        if not custom_path.is_dir():
            raise InvalidPackagePath(f"Invalid path: {custom_path}")
        return (PackageSpec(name=custom_path.name, path=custom_path),)

    if use_all:
        if not src_root.exists():
            raise InvalidPackagePath("Missing 'src/' directory in project root.")
        return tuple(
            PackageSpec(name=p.name, path=p)
            for p in src_root.iterdir()
            if (p / "__init__.py").exists()
        )

    if not package_names:
        raise InvalidPackagePath("No packages specified. Provide a name, a --path, or use --all.")

    specs = []
    for name in package_names:
        path = src_root / name
        if not (path / "__init__.py").exists():
            raise InvalidPackagePath(f"Invalid package: {name} not found in src/")
        specs.append(PackageSpec(name=name, path=path))

    return tuple(specs)
