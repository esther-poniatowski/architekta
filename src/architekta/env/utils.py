""" """

import os
import sysconfig
from pathlib import Path
from typing import Optional, List


def get_site_packages() -> Path:
    path = sysconfig.get_paths()["purelib"]
    return Path(path)


def is_current_conda_env(name: str) -> bool:
    return os.environ.get("CONDA_DEFAULT_ENV") == name


def is_base_conda_env() -> bool:
    conda_prefix = os.environ.get("CONDA_PREFIX")
    return conda_prefix and Path(conda_prefix).name == "base"


def resolve_package_paths(
    package_names: List[str], use_all: bool, custom_path: Optional[Path]
) -> dict:
    src_root = Path.cwd() / "src"

    if custom_path is not None:
        if not custom_path.is_dir():
            raise ValueError(f"Invalid path: {custom_path}")
        name = custom_path.name
        return {name: custom_path}

    if use_all:
        if not src_root.exists():
            raise ValueError("Missing 'src/' directory in project root.")
        return {p.name: p for p in src_root.iterdir() if (p / "__init__.py").exists()}

    if not package_names:
        raise ValueError("No packages specified. Provide a name, a --path, or use --all.")

    pkg_dirs = {}
    for name in package_names:
        path = src_root / name
        if not (path / "__init__.py").exists():
            raise ValueError(f"Invalid package: {name} not found in src/")
        pkg_dirs[name] = path

    return pkg_dirs
