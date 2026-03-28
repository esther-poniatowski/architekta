# Architekta

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](#installation)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/architekta)](https://github.com/esther-poniatowski/architekta/commits/main)
[![Python](https://img.shields.io/badge/python-supported-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

---

Automates Python development tasks from setup to deployment through a unified CLI.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Support](#support)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview

### Motivation

Managing a Python project from setup to deployment requires coordinating many tools and tasks:
managing dependencies, testing, linting, documenting, and packaging.

Without an integrated framework, these tasks rely on disparate tools and ad hoc workflows,
which fragments project structure and increases maintenance cost.

Existing solutions address isolated aspects (see [ALTERNATIVES.md](docs/ALTERNATIVES.md)),
but none integrates all stages into a coherent system built around Python.

### Advantages

Architekta consolidates development operations into a unified interface:

- **Unified task coordination**: Single interface to set up environments, test, lint, document,
  and package.
- **Automated workflows**: Predefined task sequences that reduce manual steps and ensure
  reproducible builds.
- **Consistent project structure**: Standardized configuration and directory layouts across
  projects.
- **Modular customization**: Plugin support and overridable task definitions for needs specific
  to each project.
- **Centralized configuration**: Single source of truth for all tool settings.
- **Built-in quality checks**: Defaults that enforce reproducible builds, code quality, test
  coverage, and documented APIs.

---

## Features

- **Virtual Environment and Dependency Management**:

  - [ ] Synchronize Conda specifications (`meta.yaml` and `environment.yaml` files) with `pyproject.toml`.
  - [ ] Update the project dependencies as new tools are added.
  - [ ] Install packages in "editable" mode.
  - [ ] Install executable scripts in "editable" mode.
  - [ ] Inspect the Conda environment for current developing packages and executables.

- **Version Control**
  - [ ] Configure Git repository to use a local commit message template.

- **Configuration**
  - [ ] Centralize modular configuration files in a `config/` directory.
  - [ ] Synchronize overlapping configurations across tools.
  - [ ] Override tool behavior with new settings (e.g. "force-exclude" in `mypy`).

---

## Installation

### Using pip

Install from the GitHub repository:

```bash
pip install git+https://github.com/esther-poniatowski/architekta.git
```

### Using conda

Install from the eresthanaconda channel:

```bash
conda install architekta -c eresthanaconda
```

### From Source

1. Clone the repository:

      ```bash
      git clone https://github.com/esther-poniatowski/architekta.git
      ```

2. Create a dedicated virtual environment:

      ```bash
      cd architekta
      conda env create -f environment.yml
      ```

---

## Usage

### Command Line Interface (CLI)

Install all packages under `src/` in editable mode into the current conda environment:

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

Display version and platform diagnostics:

```sh
architekta info
```

### Programmatic Usage

```python
from architekta.env.utils import get_site_packages, resolve_package_paths

# Find the site-packages directory for a conda environment
site_dir = get_site_packages("myenv")

# Resolve package paths from the src/ directory
paths = resolve_package_paths(packages=["pkg_a", "pkg_b"])
```

---

## Configuration

### Environment Variables

|Variable|Description|Default|Required|
|---|---|---|---|
|`VAR_1`|Description 1|None|Yes|
|`VAR_2`|Description 2|`false`|No|

### Configuration File

Configuration options are specified in YAML files located in the `config/` directory.

The canonical configuration schema is provided in [`config/default.yaml`](config/default.yaml).

```yaml
var_1: value1
var_2: value2
```

---

## Documentation

- [User Guide](https://esther-poniatowski.github.io/architekta/guide/)
- [API Documentation](https://esther-poniatowski.github.io/architekta/api/)

> [!NOTE]
> Documentation can also be browsed locally from the [`docs/`](docs/) directory.

## Support

**Issues**: [GitHub Issues](https://github.com/esther-poniatowski/architekta/issues)

**Email**: `{{ contact@example.com }}`

---

## Contributing

Please refer to the [contribution guidelines](CONTRIBUTING.md).

---

## Acknowledgments

### Authors & Contributors

**Author**: @esther-poniatowski

**Contact**: `{{ contact@example.com }}`

For academic use, please cite using the GitHub "Cite this repository" feature to
generate a citation in various formats.

Alternatively, refer to the [citation metadata](CITATION.cff).

### Third-Party Dependencies

- **[Library A](link)** - Purpose
- **[Library B](link)** - Purpose

---

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).
