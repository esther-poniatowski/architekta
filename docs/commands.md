# Commands

## Command: `env install-editable`

**Description**: Install package(s) in "editable mode" in the active conda environment. This
operation allows the package to be imported directly from its source directory, enabling immediate
reflection of source code modifications without requiring reinstallation.

Technically, the command creates a `.pth` file in the `site-packages` directory of the active conda
environment, containing the path to the package directory. The `.pth` file is named `<package>.pth`
and will be overwritten if it exists, ensuring unique package names and avoiding conflicts with
other packages. If the `--include-tests` option is specified (see below), the `.pth` file will also
include the path to the test directory.

This is an alternative to using `pip install -e .` for editable installations in conda environments,
thereby avoiding the need to build the package as a wheel or source distribution.

**Inputs**:

- Positional argument(s): Package name(s) to install, when the command is run in the root directory
  of the project and the package is in the standard `src` layout. If neither `--path` nor `--all`‡ is
  specified, at least one package name must be provided as a positional argument.

- `--all` (optional, default=False): Install all packages located in the `src/` directory in
  editable mode.

- `--path PATH` (optional): Path to the package directory, if not in the standard layout. If
  specified, the command operates in single-package mode and ignores other positional arguments or
  `--all`.

- `--include-tests` (optional, default=False): Include the test directory in the editable
  installation of the package.

- `--env ENV` (optional): Specify the conda environment to install into. Defaults to the currently
  active environment.

- `--force` (optional, default=False): Reinstall even if already installed in editable mode. Useful
  to update paths when the package location has changed.

- `--dry-run` (optional, default=False): Preview the paths that would be added without modifying the
  environment.

**Outputs**:

- Exit codes:

| Code | Condition                                            |
| ---- | ---------------------------------------------------- |
| 0    | Success                                              |
| 1    | Invalid paths or package names                       |
| 2    | Missing `src` layout in the project directory        |
| 3    | Package conflict                                     |
| 4    | Nonexistent Conda environment                        |
| 5    | Attempted modification of the base Conda environment |

- Diagnostic messages indicating success or failure of the installation. All diagnostic messages are
  written to stderr.

**Side Effects**: Creates or updates a `.pth` file in the `site-packages` directory of the active
conda environment. This modification is persistent and will affect Python import resolution until
the `.pth` file is removed.

**Dependencies**:

- Assumes an active Conda environment and write permissions to its `site-packages`.

**Use cases**:

- Initial development of a package, allowing updates without reinstalling.
- Maintaining inter-package dependencies in monorepo structures during development.
- Testing or documentation environments where source availability is required without packaging.
