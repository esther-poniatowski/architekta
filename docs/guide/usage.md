# Usage

Architekta consolidates Python development operations into a unified CLI. The
tool automates environment setup, dependency synchronization, and project
configuration across the development lifecycle.

For the full command registry, refer to [CLI Reference](cli-reference.md). For
configuration options, refer to [Configuration](configuration.md).

## Installing Packages in Editable Mode

Install all packages under `src/` into the current conda environment:

```sh
architekta env install-editable --all
```

Install a single package with a dry-run preview:

```sh
architekta env install-editable --path ./src/my_package --dry-run
```

Target a specific conda environment:

```sh
architekta env install-editable --all --env myenv
```

## Inspecting the Environment

Display the packages and executables installed in the current environment:

```sh
architekta env inspect
```

## Synchronizing Dependencies

Synchronize Conda specifications (`meta.yaml` and `environment.yaml`) with
`pyproject.toml` to keep dependency declarations consistent:

```sh
architekta deps sync
```

## Configuring Version Control

Set up the Git repository to use a local commit message template:

```sh
architekta git setup
```

## Programmatic API

The same functionality is accessible from Python:

```python
from architekta.env.utils import get_site_packages, resolve_package_paths

# Find the site-packages directory for a conda environment
site_dir = get_site_packages("myenv")

# Resolve package paths from the src/ directory
paths = resolve_package_paths(packages=["pkg_a", "pkg_b"])
```

## Next Steps

- [CLI Reference](cli-reference.md) — Full command registry and options.
- [Configuration](configuration.md) — Configuration files and environment variables.
