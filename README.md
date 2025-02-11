# Architekta

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License:MIT](https://img.shields.io/badge/License-GNU-yellow.svg)](https://opensource.org/licenses/GNU)

Architekta automates Python project setup and management by integrating multiple development tools
into a unified workflow.

## Motivation

Setting up a new Python project often involves fragmented, time-consuming steps: initializing
repositories, configuring environments, and setting up development tools. Existing solutions
address specific tasks but do not provide a unified, Python-centric approach (e.g., Tox for testing,
Buildout for assembly, Ansible for deployment, conda-env-builder for Conda environment building...).

Architekta consolidates these processes into a single toolkit, ensuring a streamlined, consistent,
and reproducible project setup. It enforces recommended practices while remaining flexible to
accommodate custom configurations. Using this toolkit, developers can focus on building their
projects rather than managing setup complexities.

Key advantages of Architekta include:

- Efficiency: Automates project management through a single interface and predefined setups,
  reducing repetitive manual tasks and eliminating the need to master multiple tools.
- Standardization: Promotes uniform directory structures and tool configurations across projects,
  facilitating collaboration onboarding.
- Customization: Offers flexible configuration options, allowing projects to adapt to specific
  requirements while maintaining standardized practices.
- Robustness: Minimizes the risk of manual setup errors and conflicts between individual project's
  components by providing structured templates and a consistent interface for multiple tools.
- Maintainability: Centralized configuration management simplifies project updates and version
  control, ensuring long-term consistency.

## Features

- **Automated Project Initialization**
  Create standardized project structures with essential directories and files.

- **Git Integration**
  Automatic repository setup with templates for:
  - `.gitignore`
  - Commit message template
  - Issue templates
  - CI/CD workflows

- **Conda Environment Management**
  Set up Conda environments with automatic path configuration.

- **Tool Configuration Templates**
  Pre-configured templates for:
  - Static code analysis (mypy, pylint)
  - Formatting (black, isort)
  - Testing (pytest)
  - Documentation (Sphinx)

- **Documentation Generation**
  Automated documentation generation with Sphinx.

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
