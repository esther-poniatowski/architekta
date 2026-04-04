# Architekta

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](docs/guide/installation.md)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/architekta)](https://github.com/esther-poniatowski/architekta/commits/main)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL--3.0-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Automates common Python development tasks through a unified CLI: environment
management, metadata synchronization, and cross-surface project renaming.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview

Setting up and maintaining a Python project involves repetitive manual steps —
installing packages in development mode, keeping metadata in sync across
GitHub and `pyproject.toml`, and renaming a project across every surface where
its name appears.  Architekta consolidates these operations into a single
command-line tool so that each task runs reliably with one invocation.

### Motivation

Each of these tasks — editable installs, metadata synchronization, cross-surface
renaming — relies on ad-hoc scripts or manual commands spread across multiple
tools.  Errors compound when steps are forgotten or executed inconsistently, and
the cost grows with the number of surfaces a project name touches (filesystem,
GitHub, conda, workspace files, submodules, in-file references).

### Advantages

- **Single entry point** — one CLI consolidates environment setup, metadata
  synchronization, and cross-surface rename.
- **Dry-run on every operation** — all commands support `--dry-run` to preview
  changes before applying them.
- **Cross-surface coordination** — the rename pipeline propagates a name change
  across filesystem, GitHub, conda, VS Code workspaces, submodules, and in-file
  references in one invocation.
- **Lightweight editable installs** — `.pth`-based mechanism avoids wheel and
  source distribution builds required by `pip install -e`.
- **README-driven metadata** — descriptions propagate from README first sentences
  to GitHub and `pyproject.toml`, keeping metadata consistent without manual
  duplication.

---

## Features

### Environment management

- [x] Install packages in editable mode via `.pth` files, discover packages
  under `src/`, and validate conda environments.
- [ ] Install executable scripts in editable mode via symlinks in the conda
  environment `bin/` directory.
- [ ] Display packages and executables installed in the current conda
  environment.
- [ ] Synchronize Conda specifications with `pyproject.toml` to keep dependency
  declarations consistent.

### Metadata and version control

- [x] Extract the first prose sentence from each project's README and propagate
  descriptions to GitHub repositories and `pyproject.toml` fields.
- [ ] Configure a Git repository to use a local commit message template.

### Cross-surface rename

- [x] Rename a project across filesystem, GitHub, conda, VS Code workspaces,
  submodules, and in-file references through a nine-stage pipeline.
  - Propagate changes to affected projects specified via `--affected-path`.
  - Preview the full plan with `--dry-run` before applying any mutation.

### Configuration

- [ ] Centralize modular configuration files in a `config/` directory and
  synchronize overlapping settings across tools.
- [ ] Override tool behavior with custom settings (e.g. `force-exclude` in
  mypy).
- [ ] Define custom command aliases in a central manifest that route to the
  tools involved in the workspace through a uniform interface, replacing ad-hoc
  invocations.

---

## Quick Start

### CLI

```sh
architekta env install-editable --all
```

```sh
architekta github sync-descriptions --dry-run
```

```sh
architekta rename old-name new-name --dry-run
```

### Application Programming Interface

```python
from architekta import info

print(info())
# architekta 0.0.0 | Platform: Darwin Python 3.12.8
```

---

## Documentation

| Guide | Content |
| ----- | ------- |
| [Installation](docs/guide/installation.md) | Prerequisites, pip/conda/source setup |
| [Usage](docs/guide/usage.md) | Workflows and detailed examples |
| [CLI Reference](docs/guide/cli-reference.md) | Full command reference and options |
| [Configuration](docs/guide/configuration.md) | Configuration files and environment variables |

---

## Contributing

Contribution guidelines are described in [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Acknowledgments

### Authors

**Author**: @esther-poniatowski

For academic use, the GitHub "Cite this repository" feature generates citations in
various formats. The [citation metadata](CITATION.cff) file is also available.

---

## License

This project is licensed under the terms of the
[GNU General Public License v3.0](LICENSE).
