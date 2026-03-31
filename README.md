# Architekta

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](docs/guide/installation.md)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/architekta)](https://github.com/esther-poniatowski/architekta/commits/main)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Automates Python development tasks from setup to deployment through a unified CLI.

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

### Motivation

Managing a Python project from setup to deployment requires coordinating many tools
and tasks: dependency management, testing, linting, documentation, and packaging.
Without an integrated framework, these tasks rely on disparate tools and ad-hoc
workflows, fragmenting project structure and increasing maintenance cost.

### Advantages

- **Unified task coordination** — single entry point for environment setup, testing,
  linting, documentation, and packaging.
- **Automated workflows** — predefined task sequences that reduce manual steps and
  ensure reproducible builds.
- **Consistent project structure** — standardized configuration and directory layouts
  across projects.
- **Centralized configuration** — single source of truth for all tool settings.

---

## Features

- [ ] **Virtual environment and dependency management**: Synchronize Conda
  specifications with `pyproject.toml`, install packages and scripts in editable mode,
  inspect the environment for installed packages.
- [ ] **Version control**: Configure Git repository to use a local commit message
  template.
- [ ] **Configuration**: Centralize modular configuration files in a `config/`
  directory, synchronize overlapping configurations across tools.

---

## Quick Start

Install all packages under `src/` in editable mode:

```sh
architekta env install-editable --all
```

Display version and platform diagnostics:

```sh
architekta info
```

---

## Documentation

| Guide | Content |
| ----- | ------- |
| [Installation](docs/guide/installation.md) | Prerequisites, pip/conda/source setup |
| [Usage](docs/guide/usage.md) | Workflows and detailed examples |
| [CLI Reference](docs/guide/cli-reference.md) | Full command registry and options |
| [Configuration](docs/guide/configuration.md) | Configuration files and environment variables |

Full API documentation and rendered guides are also available at
[esther-poniatowski.github.io/architekta](https://esther-poniatowski.github.io/architekta/).

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
