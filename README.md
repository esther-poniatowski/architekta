# Architekta

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-linux%20|%20windows%20|%20macos-lightgrey)]()
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)
[![GitHub last commit](https://img.shields.io/github/last-commit/esther-poniatowski/architekta)](https://github.com/esther-poniatowski/architekta/commits/main)

Project manager for automating the entire lifecycle of Python projects, from initial setup to
deployment. It provides a standardized interface and project structure to control development tasks
and configurations across multiple tools.

## Motivation

Managing a Python project throughout its life cycle, from initial setup to deployment, involves a
sequence of tasks (e.g. dependency management, testing, linting, documentation, packaging).

These tasks often require diverse of tools and configurations, leading to overwhelming workflows
and patchwork project structures. While existing solutions address isolated aspects of project
management (see [ALTERNATIVES.md](docs/ALTERNATIVES.md)), no tool unifies the entire workflow into a
single, Python-centric framework.

Architekta consolidates these operations into a comprehensive project management system.

General features include:

- Control: High-level interface to manage an entire project lifecycle (setup, development,
  deployment, distribution).
- Integration: Seamless orchestration of multiple tools (environment management, testing, linting,
  documentation, packaging).
- Automation: Predefined tasks and setups to reduce manual intervention.
- Robustness: Promotion of recommended practices for reproducibility, extensibility, code quality,
  testing, documentation.
- Standardization: Consistent workflows and configuration structure to facilitate collaboration and
  onboarding.
- Customization: Flexible configurations and plugin support to adapt to specific project needs.
- Maintainability: Central configuration to simplify future updates or extensions.

## Features

- **Project Structure**
  - Centralize project metadata, dependencies and tool configurations in a declarative format
    (`arkt.conf`).
  - Create standardized directories structures: `src/`, `tests/`, `docs/`, `config/`, `scripts/`.
  - Generate essential files: `README.md`, `LICENSE`.

- **Version Control**
  - Configure Git repository: `.gitignore`, commit message template.
  - Configure Github repository: issue templates, GitHub actions.

- **Virtual Environment and Dependency Management**
  - Ensure dependency isolation and resolution with Conda.
  - Create and update the Conda environment from a `environment.yml` file, automatically generated
    to integrates essential development tools (aligned with recommended practices) and project's
    specific dependencies (user-defined).
  - Register in "editable" mode the project packages (in the Python search path or the conda
    environment, via a `.pth` file in `site-package`), and executable scripts (in the conda
    environment `bin`, via a symlink).
  - Inspect the Conda environment.

- **Code Quality**
  Provides default configuration templates for:
  - Type checking with Mypy
  - Linting with Pylint
  - Formatting with Black

- **Testing**
  - Provide a default configuration template for Pytest (`conftest.py`).
  - Generate reports for test results and coverage, to be integrated with Sphinx documentation.

- **Documentation**
  - Automated documentation generation with Sphinx, API documentation with autodoc.
  - Templates for Architecture Decision Records (ADR).
  - Assistance in changelog generation.

- **Versioning**
  - Automate versioning numbering and tagging following the semantic versioning scheme.
  - Assist in release notes and changelog aggregation.
  - Synchronize with GitHub releases.

- **Distribution**
  - Build and package the project for distribution via both PyPI and Conda (generate
    `pyproject.toml` and `meta.yaml` files).
  - Define GitHub workflows for CI/CD, automating test, build, and deploy steps.

- **IDE Integration**
  - Generate a VSCode workspace to integrate all the tools and configurations.

## Installation

Architekta is currently available for installation directly from its GitHub repository.

To install the package and its dependencies in an activated virtual environment:

```sh
pip install git+https://github.com/esther-poniatowski/architekta.git
```

To install a specific version, specify the version tag in the URL:

```sh
pip install git+https://github.com/esther-poniatowski/architekta.git@v0.1.0
```

## Quick Start

1. Initialize new project (`project-name`):

    ```sh
    architekta init <project-name>
    ```

2. Edit `config/architekta_config.ini`:

    ```ini
    [project]
    name = my_project
    python_version = 3.10

    [tools]
    enable_linting = true
    enable_testing = true
    ```

3. Configure components:

    ```sh
    architekta setup git
    architekta tool black
    architekta env create
    ```

## Command Reference

| Command | Description |
|---------|-------------|
| `init [name]` | Initialize new project structure |
| `setup [component]` | Configure project components (git/conda/docs) |
| `tool [name]` | Add tool configuration (mypy/pylint/black) |
| `env [action]` | Manage Conda environments (create/update/export) |
| `generate docs` | Build project documentation |

## License

This project is licensed under the [GNU LICENSE](LICENSE).
