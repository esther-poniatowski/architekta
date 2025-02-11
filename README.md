# Architekta

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-GNU-yellow.svg)](https://opensource.org/licenses/GNU)

Automation toolkit for streamlined Python project setup with centralized configuration of Git repositories,  Conda environments, and development tools.

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


## Installation

```
pip install architekta
```

## Quick Start

1. Initialize new project (`project-name`) :
```
architekta init <project-name>
```

2. Edit `config/architekta_config.ini`:
```
[project]
name = my_project
python_version = 3.10

[tools]
enable_linting = true
enable_testing = true
```

3. Configure components:
```
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

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

