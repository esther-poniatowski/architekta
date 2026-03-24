# Commands

## Command: `env install-editable`

**Description**: Install package(s) in "editable mode" in the active conda environment. The
installed package can be imported directly from its source directory, so that changes to the source
code take effect immediately without reinstalling.

Technically, the command creates a `.pth` file in the `site-packages` directory of the active conda
environment, containing the path to the package directory. The `.pth` file is named `<package>.pth`
and will be overwritten if it exists, ensuring unique package names and avoiding conflicts with
other packages. If the `--include-tests` option is specified (see below), the `.pth` file will also
include the path to the test directory.

Unlike `pip install -e .`, the `.pth` approach does not require building the package as a wheel or
source distribution.

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

## Command: `github sync-descriptions`

**Description**: Synchronize each project's first descriptive sentence from `README.md` into two
targets: the GitHub repository description ("About" field) and the `description` field in
`pyproject.toml`. Iterates over sibling project directories, extracts the first line of prose from
each README, and updates both targets when they differ.

The extraction skips title headings, badge lines (`[![`), horizontal rules (`---`), HTML comments,
and blank lines, returning the first line of plain prose.

Each target is synchronized independently. A missing `pyproject.toml` or absent `description` field
causes the pyproject target to be skipped for that project without affecting the GitHub target.

**Inputs**:

- Positional argument(s) (optional): Path(s) to project directories to synchronize. If omitted, the
  command discovers all sibling directories of the current working directory that contain both a
  `README.md` and a `.git` directory.

- `--dry-run` (optional, default=False): Preview the changes that would be made without updating any
  GitHub repository descriptions.

**Outputs**:

- Exit codes:

| Code | Condition                                        |
| ---- | ------------------------------------------------ |
| 0    | All descriptions synchronized successfully       |
| 1    | One or more projects failed (skipped or errored) |

- Diagnostic messages for each project and target, written to stderr. Each line includes the
  project name and the target (`[github]` or `[pyproject]`):

| Prefix  | Meaning                                                  |
| ------- | -------------------------------------------------------- |
| `[OK]`  | Target description already matches the README            |
| `[SET]` | Target description updated to match the README           |
| `[DRY]` | Dry-run preview of the change                            |
| `[SKIP]`| Target skipped (no remote, no pyproject.toml, or error)  |
| `[ERR]` | Update failed (GitHub API error or file write error)     |

**Side Effects**:

- Updates the "description" field of the GitHub repository via `gh repo edit`. The change is
  immediately visible on the repository's GitHub page.
- Rewrites the `description = "..."` line in `pyproject.toml` in place, preserving all other
  file content.

**Dependencies**:

- Requires the GitHub CLI (`gh`) to be installed and authenticated (`gh auth login`).
- Each project directory must have a git remote named `origin` pointing to a GitHub repository.
