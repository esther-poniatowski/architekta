# Architekta

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](#installation)
[![Maintenance](https://img.shields.io/maintenance/yes/2025)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/architekta)](https://github.com/esther-poniatowski/architekta/commits/main)
[![Python](https://img.shields.io/badge/python-supported-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

---

Project manager for standardizing and automating Python development workflows via centralized configuration, predefined task orchestration, and modular extensibility.

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

Managing a Python project throughout its life development cycle, from initial setup to deployment,
requires coordinating heterogeneous tools, configurations and tasks (e.g. dependency management,
testing, linting, documentation, packaging).

In the absence of an integrated framework, these tasks are typically handled using disparate tools
and ad hoc workflows, leading to fragmented project structures, increased maintenance burden, and
inconsistent development practices.

Existing solutions address isolated aspects of project management (see
[ALTERNATIVES.md](docs/ALTERNATIVES.md)), but no framework unifies integrates all stages into a
coherent Python-centric system.

### Advantages

Architekta introduces a centralized and extensible project management system that consolidates
common development operations into a unified interface.

It provides the following benefits:

- **Integrated orchestrations**: Uniform interface to coordinate multiple development tasks
  (environment setup, testing, linting, documentation, packaging).
- **Automated workflows**: Predefined task sequences to reduce manual intervention and ensure
  reproducible behaviors.
- **Standardized structure**: Consistent configuration schemes and directory layouts to facilitate
  collaboration and onboarding.
- **Flexible customization**: Modular task definitions and plugin support for project-specific
  overrides and extensions.
- **Centralized maintenance**: Single source of truth for configuration to improve control and
  long-term updates.
- **Built-in compliance with development standards**: Integrated checks and defaults promoting
  reproducibility, code quality, test coverage, documentation.

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

To install the package and its dependencies, use one of the following methods:

### Using Pip Installs Packages

Install the package from the GitHub repository URL via `pip`:

```bash
pip install git+https://github.com/esther-poniatowski/architekta.git
```

### Using Conda

Install the package from the private channel eresthanaconda:

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

To display the list of available commands and options:

```sh
architekta --help
```

### Programmatic Usage

To use the package programmatically in Python:

```python
import architekta
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
