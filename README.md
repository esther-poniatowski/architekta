# Architekta

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License:MIT](https://img.shields.io/badge/License-GNU-yellow.svg)](https://opensource.org/licenses/GNU)

Architekta is a unified Python project manager focused on enforcing and automating the recommended
practices for robustness and reproducibility. It guides the entire project lifecycle through setup,
development, versioning, and distribution, integrating multiple development tools into a cohesive
workflow.

## Motivation

Managing a Python project throughout its life cycle involves a complex sequence of tasks, fragmented
across multiple tools and configurations.

While existing solutions address individual aspects (see [ALTERNATIVES.md](docs/ALTERNATIVES.md) for
comparisons), no tool unifies the entire workflow into a single, Python-centric framework.

Architekta provides a comprehensive project management system that:

- Automates recommended practices across the project lifecycle.
- Enforces a consistent structure and toolchain setup.
- Reduces friction by integrating multiple tools into a single interface.

With Architekta, developers can focus on implementing their project's logic, rather than on
configuring tooling.

Key advantages of Architekta include:

- Integration: Unifies project setup, development, and distribution in a structured framework.
- Automation: Eliminates repetitive setup tasks and minimizes the need to learn multiple independent
  tools.
- Robustness: Integrates multiple tools to enforce recommended practices for reproducibility,
  code quality, testing, documentation, etc.
- Standardization: Promotes uniform practices across projects, facilitating collaboration and
  onboarding.
- Efficiency: Automates project management through a single interface and predefined setups,
  reducing repetitive manual tasks and eliminating the need to master multiple tools.
- Customization: Offers flexible configurations to adapt to project-specific requirements.
- Maintainability: Centralized configuration management simplifies project updates and extensions.


## Features

- **Project Structure**
  - Centralize project metadata, dependencies and tool configurations in a declarative format (`arkt.conf`).
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
  - Formatting with Black and Isort

- **Testing**
  - Provide a default configuration template for Pytest (`conftest.py`).
  - Generate reports for test results and coverage, to be integrated with Sphinx documentation.

- **Documentation**
  - Automated documentation generation with Sphinx, API documentation with autodoc.
  - Templates for Architecture Decision Records (ADR).
  - Assistance in changelog generation.

- **Versionning**
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

```sh
pip install architekta
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
