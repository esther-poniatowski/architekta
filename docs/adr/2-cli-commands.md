# ADR 0001: CLI Commands

**Status**: Proposed

---

## Problem Statement

Decide what commands should be available to fulfill the target functionalities of the application.

**Questions to be addressed**:

1. What commands should be available to users?
2. Should the application be run with its full name (`architekta`) or a shorter alias (`arkt`)? Is
   it possible to provide both options?
3. How should the commands be structured and named?

---

## Decisions

- Implement each subcommand as a separate function using the `typer` library.
- Provide a central entry point in `cli.py`, but organize commands in modular files.
- If possible, allow running the application both with its full name (`architekta`) or a shorter
  alias (`arkt`).
- Offer a `--help` option for each command to display usage information (if not already provided by
  `typer`).
- Implement a `-v` or `--verbose` flag to provide detailed output during command execution.
- Dry run: Add a `--dry-run` option for commands that make changes, allowing users to see what would
  happen without actually making changes.


## Commands by functionality

### Core Commands

**Help command:**

- Display a list of available commands and options.

```sh
architekta --help
```

**Check the project's state**

- Ensures that users can check what's missing or outdated before running update.
- Checks whether required directories/files are missing.
- Reports configuration mismatches between `arkt.conf` and actual project structure.
- Lists pending updates (dependencies, documentation, versioning).
- Checks if `VERSION` is properly incremented compared to tags.

```sh
architekta inspect [env | config | deps | docs | version]
```

**Update the whole project after any change in configurations:**

- Check the current state of the project compared to the configuration files.
- Update the project structure, files, and configurations accordingly.

```sh
architekta update [env | config | deps | docs | version]
```

### Initialization

**Initialize a new project with a standardized structure:**

- To be run within an existing directory named after the project. This is important so that it can
  be used within an existing repository cloned from a github repository.
- Create the central configuration file: `arkt.conf`.
- Create  `config` directory with `dependencies/`: `runtime.yml`, `development.yml`

```sh
architekta init
```

**Initialize and populate a standardized structure:**

- Create project directories: `src`, `tests`, `docs`, `scripts` (if not present)
- In the root directory:
  - Essential files: `README.md`, `LICENSE` (if not present)
  - VS Code workspace file: `.code-workspace` (if not present)
  - `VERSION` file for versioning
- In `src` directory:
  - Template files for the main project code (e.g., `__init__.py`, `main.py`)
- In `tests` directory:
  - Template files for Pytest configuration (e.g., `conftest.py`)
  - Template test files (e.g., `test_.py`)
- In `docs` directory:
  - In `source/`:
    - `conf.py`
    - `index.rst`
    - `changelog.rst`
    - subdirectories: `api/`, `release_notes/`, `adr/` (Architecture Decision Records (ADR)) +
      respective template files
    - `_templates/` + template files for documentation
    - `_static/` (empty)
  - In `build/`: `html/` subdirectory for the generated documentation
  - In `release/`: Template file for release notes
- In `config` directory:
  - In `tools/`: Template configuration file for each tool (e.g., `mypy.ini`, `pylint.ini`)
  - In `dictionaries/`: Set of dictionaries for spell checking (Cspell)
- In `scripts` directory:
  - Template script for the main entry point of the project (e.g., `main.py`)

```sh
architekta setup structure
```


### Version Control

**Initialize and Configure Git repository:**

- Initialize a new Git repository (if not present).
- Display useful repository information: user name, email, remote URLs.
- Add a template `.gitignore` file (which takes into account the specified tools in the central
  configuration file).
- Configure the commit message template.

```sh
architekta setup repo --git
```

**Initialize and Configure GitHub repository:**

- Create a new repository on GitHub (if not present) by pushing the local repository.
- Create `.github/` directory.
- Add issue templates.
- Add CI/CD workflows (based on the specifications of the central configuration file).

```sh
architekta setup repo --github
```

**Combine both Git and GitHub setup:**

- Initialize and configure both the local and remote repositories.

```sh
architekta setup repo
```

### Virtual Environment and Dependency Management

**Initialize a Conda environment from the configuration file:**

- Generate the `environment.yml` file combining essential development tools
  (`dependencies/development`) and project's specific dependencies (`dependencies/runtime`).
- Create the Conda environment from the `environment.yml` file.
- Register in "editable" mode the project packages (in the Python search path or the conda
  environment, via a `.pth` file in `site-package`), and executable scripts (in the conda
  environment `bin`, via a symlink).

```sh
architekta setup env
```

**Update a Conda environment after changes in dependencies:**

- Update the `environment.yml` file with the new dependencies.
- Update the Conda environment.

```sh
architekta update env
```

**Inspect the Conda environment:**

- Check the presence of a `.pth` file in the `site-package` directory.
- Show the directories registered in "editable" mode.
- Display the list of packages installed in the Conda environment.

```sh
architekta inspect env
```

All the commands above can be subdivide into more specific commands with options:

- `--deps` to only setup / update / display the dependencies.
- `--registered` to only setup / update / display the registered paths.

### Code Artifacts

**Code checking with all tools (mypy, pyling, blaock, isort):**

- Run all the code quality tools on the project.
- Generate reports for each tool.

```sh
architekta code check
```

**Run tests with Pytest:**

- Generate reports for test results and coverage, to be integrated with Sphinx documentation.

```sh
architekta code test
```

**Generate documentation with Sphinx:**

- Automated documentation generation with Sphinx, API documentation with autodoc.

```sh
architekta code docs
```

**Clean the project (remove temporary files, cache, etc.):**

- Remove all temporary files and directories generated by the tools.

```sh
architekta clean
```

### Versionning

**Automate versioning numbering and tagging:**

- Adjust the version number in the `VERSION` file.
- Adjust the version number in all the relevant files.
- Create a release notes to fill in.
- Add en entry in the changelog pointing to the new release note.
- Create a tag for the new version.
- Synchronize with GitHub releases.

```sh
architekta version increment [--major | --minor | --patch]
architekta version tag
architekta version release
```

### Distribution

**Prepare the package for distribution:**

- If PyPI: generate the `pyproject.toml` file.
- If Conda: generate `meta.yaml` file.

```sh
architekta dist prepare [--pypi | --conda]
```

**Build and package for distribution:**

- If PyPI: build the package and upload it to PyPI, using the `twine` package (or `hatch`?).
- If Conda: build the package and upload it to the Conda-forge repository.

```sh
architekta dist build [--pypi | --conda]
```

**Run the CI/CD pipeline:**

- Run GitHub workflows for CI/CD, automating test, build, and deploy steps.

```sh
architekta ci
```


## Summary

Commands structure :

- `architekta` or `arkt` (alias)
- `init`          -> `core` module
- `clean`         -> `code` module
- `inspect`       -> Subcommand group
  - `env`         -> `env` module (for paths)
  - `deps`        -> `env` module
  - `config`      -> `config` module
  - `docs`        -> `docs` module
  - `version`     -> `version` module
- `setup`         -> Subcommand group
  - `structure`   -> `core` module
  - `repo`        -> `repo` module
    - `--git`
    - `--github`
  - `env`         -> `env` module
- `update`        -> Subcommand group
  - `env`         -> `env` module (for paths)
  - `deps`        -> `env` module
  - `config`      -> `core` module
  - `docs`        -> `code` module
  - `version`     -> `version` module
- `code`          -> Subcommand group
  - `test`        -> `code` module
  - `docs`        -> `code` module
  - `check`       -> `code` module
- `version`       -> Subcommand group
  - `increment`        -> `version` module
    - `--major`
    - `--minor`
    - `--patch`
  - `tag`         -> `repo` module or `version` module
  - `release`     -> `repo` module or `version` module
- `dist`          -> Subcommand group
  - `prepare`     -> `actions` module ?
    - `--pypi`
    - `--conda`
  - `build`       -> `actions` module ?
    - `--pypi`
    - `--conda`
- `ci`            -> `actions` module ?


architekta --help                # General help
architekta setup project         # Project initialization
architekta setup structure       # Create directories & config files
architekta setup env             # Create Conda environment
architekta setup deps            # Manage dependencies
architekta inspect env           # Check Conda environment state
architekta inspect config        # Check project configuration
architekta update env            # Apply environment fixes
architekta update deps           # Apply dependency updates
architekta test run              # Run Pytest
architekta docs build            # Generate documentation

architekta version increment     # Increment version number
architekta version tag           # Create Git tag
architekta version release       # Create GitHub release
architekta dist prepare          # Prepare for distribution
architekta dist build            # Build package
architekta ci run                # Run CI/CD pipeline


- `init`          -> `core` module
- `inspect`       -> Subcommand group
  - `env`         -> `env` module (for paths)
    - `--deps` to only display installed dependencies
      - `--pip` to only display packages installed with pip within conda environment
    - `--registered` to only display the registered paths in editable mode
      - `--packages` to only display the registered packages
      - `--scripts` to only display the registered scripts
  - `config`      -> `config` module
  - `docs`        -> `docs` module
  - `version`     -> `version` module
- `setup`         -> Subcommand group
  - `structure`   -> `core` module
  - `repo`        -> `repo` module
    - `--git`
    - `--github`
  - `env`         -> `env` module
    - `--deps` to only setup install dependencies
    - `--registered` to only register package and script paths in editable mode
- `update`        -> Subcommand group
  - `env`         -> `env` module (for paths)
    - `--deps` to only update dependencies
    - `--registered` to only update the registered paths in editable mode
  - `config`      -> `core` module
- `version`       -> Subcommand group
  - `increment`        -> `version` module
    - `--major`
    - `--minor`
    - `--patch`
  - `tag`         -> `repo` module or `version` module
  - `release`     -> `repo` module or `version` module
- `dist`          -> Subcommand group
  - `prepare`     -> `actions` module ?
    - `--pypi`
    - `--conda`
  - `build`       -> `actions` module ?
    - `--pypi`
    - `--conda`
- `clean`         -> Subcommand group
  - `workspace`   -> `clean` module (remove temp files)
  - `build`       -> `clean` module (remove compiled artifacts)
  - `cache`       -> `clean` module (remove caches for python, pytest, mypy, etc.)
- `run`          -> Subcommand group
  - `tests`       -> `code` module
  - `docs`        -> `code` module
  - `checks`      -> `code` module
  - `ci`          -> `actions` module ?
