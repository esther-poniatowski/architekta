# CLI Reference

## Command: `env install-editable`

**Description**: Install package(s) in "editable mode" in the active conda environment. The
installed package can be imported directly from its source directory, so that changes to the source
code take effect immediately without reinstalling.

Technically, the command creates a `.pth` file in the `site-packages` directory of the active conda
environment, containing the path to the package directory. The `.pth` file is named `<package>.pth`.
A `.pth` file of the same name may come from another installer, so the command does not overwrite an
existing `.pth` file whose content differs from the planned one: it stops with status 2 and names
the file, unless `--force` is passed. An existing file with the planned content is left as it is, so
the command can run again. If the `--include-tests` option is
specified (see below), the `.pth` file will also include the path to the test directory.

Unlike `pip install -e .`, the `.pth` approach does not require building the package as a wheel or
source distribution.

**Inputs**:

- Positional argument(s): Package name(s) to install, from the `src/` folder of the project root, in
  the standard `src` layout. If neither `--package-dir` nor `--all` is
  specified, at least one package name must be provided as a positional argument.

- `-r`, `--root PATH` (optional): Project folder whose `src/` holds the packages. Defaults to the
  folder named by the environment variable `ARCHITEKTA_ROOT`, else to the current folder. Architekta
  has no configuration file, so the command does not search the ancestors of the current folder.

- `--all` (optional, default=False): Install all packages located in the `src/` directory in
  editable mode.

- `--package-dir PATH` (optional): Path to the package directory, if not in the standard layout,
  read from the current folder like every path given on the command line. If
  specified, the command operates in single-package mode and ignores other positional arguments or
  `--all`.

- `--include-tests` (optional, default=False): Include the test directory in the editable
  installation of the package.

- `--env ENV` (optional): Specify the conda environment to install into. Defaults to the currently
  active environment.

- `--force` (optional, default=False): Overwrite an existing `.pth` file whose content differs.
  Without this flag, the command stops with status 2 and names the file.

- `--dry-run` (optional, default=False): Preview the paths that would be added without modifying the
  environment.

**Outputs**:

- Exit codes:

| Code | Condition                                                          |
| ---- | ------------------------------------------------------------------ |
| 0    | Success                                                            |
| 2    | Usage or environment error (invalid package path, missing or base conda env, or an existing `.pth` file that differs, without `--force`) |

- Diagnostic messages indicating success or failure of the installation. All diagnostic messages are
  written to stderr.

**Side Effects**: Creates, or overwrites when `--force` is passed, a `.pth` file in the
`site-packages` directory of the active conda environment. This modification is persistent and will
affect Python import resolution until the `.pth` file is removed.

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
  `README.md` and a `.git` directory. The command takes no `--root`: it acts on several projects,
  and each path is read from the current folder.

- `--dry-run` (optional, default=False): Preview the changes that would be made without updating any
  GitHub repository descriptions.

**Outputs**:

- Exit codes:

| Code | Condition                                        |
| ---- | ------------------------------------------------ |
| 0    | All descriptions synchronized successfully       |
| 1    | One or more projects failed (skipped or errored) |
| 2    | No project directory found                       |

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

## Command: `rename`

**Description**: Rename a project across all surfaces -- filesystem, GitHub repository, conda
environment, VS Code workspaces, git submodules, and in-file references -- through a nine-stage
pipeline. Each stage plans before executing. `--dry-run` previews the full plan without applying any
mutation.

**Pipeline stages** (executed in order):

| #   | Stage      | Action                                                    |
| --- | ---------- | --------------------------------------------------------- |
| 1   | validate   | Check preconditions (paths exist, repos clean)            |
| 2   | filesystem | Rename the local project directory                        |
| 3   | git-remote | Rename the GitHub repository and update the local remote  |
| 4   | workspaces | Rename and update VS Code `.code-workspace` files         |
| 5   | conda      | Rename the conda environment (skippable)                  |
| 6   | self-refs  | Replace old name in the project's own tracked files       |
| 7   | cross-refs | Replace old name in affected sibling projects             |
| 8   | submodules | Update `.gitmodules` and sync submodule URLs              |
| 9   | commit     | Stage, commit, and optionally push all changes (skippable)|

**Inputs**:

- `OLD_NAME` (positional, required): Current project name.

- `NEW_NAME` (positional, required): Target project name.

- `-r`, `--root PATH` (optional): Path to the project directory. Defaults to the folder named by the
  environment variable `ARCHITEKTA_ROOT`, else to the current folder. Architekta has no
  configuration file, so the command does not search the ancestors of the current folder.

- `--affected-path PATH` (optional, repeatable): Path to a sibling project affected by the rename.
  The pipeline scans each affected project for cross-references. Repeat the flag for multiple
  projects: `--affected-path ../a --affected-path ../b`.

- `--alias NAME` (optional, repeatable): Former project name to replace alongside the current one.
  Repeat for multiple aliases: `--alias old-alias-1 --alias old-alias-2`.

- `--github-owner OWNER` (optional): GitHub owner/organization. Auto-detected from the `origin` git
  remote when omitted. Pass explicitly when the remote is unavailable or points to a fork.

- `--conda-env NAME` (optional): Current conda environment name. Required only when the environment
  name differs from the project name. The pipeline derives the new environment name by replacing the
  old project name within the value.

- `--workspace-file FILENAME` (optional): VS Code workspace filename (e.g. `myproject.code-workspace`).
  The pipeline renames the file and updates references inside all `.code-workspace` files under the
  workspace root.

- `--dry-run` (optional, default=False): Plan all nine stages and print the full change report
  without applying any mutation.

- `--yes` (optional, default=False): Answer yes to the confirmation. A rename changes the files of
  the researcher, so the command asks for a confirmation on a terminal; without a terminal and
  without `--yes`, it stops with status 2. `--dry-run` needs no confirmation.

- `--push` (optional, default=False): Push commits in all affected repositories after the commit
  stage.

Options may be written before, between or after the two names. An unknown option or an extra
argument is a usage error.

- `--skip STAGE` (optional, repeatable): Skip a named stage. Only skippable stages (`conda`,
  `commit`) can be skipped: `--skip conda --skip commit`.

- `--no-commit` (optional, default=False): Shorthand for `--skip commit`. Execute all stages except
  the final commit.

- `--verbose` (optional, default=False): Print each file modification and path rename as the
  pipeline executes.

**Outputs**:

- Exit codes:

| Code | Condition                                                    |
| ---- | ------------------------------------------------------------ |
| 0    | All stages completed successfully                            |
| 1    | Pipeline error or validation failure, or confirmation declined |
| 2    | Usage error, or no terminal and no `--yes`                   |

- Per-stage diagnostic messages written to stderr:

| Prefix  | Meaning                                 |
| ------- | --------------------------------------- |
| `[OK]`  | Stage completed with a change summary   |
| `[SKIP]`| Stage skipped (by user or precondition) |
| `[ERR]` | Stage failed                            |

**Side Effects**:

- Renames the project directory on the filesystem.
- Renames the GitHub repository via `gh api`.
- Renames the conda environment via `conda rename`.
- Modifies tracked files across the project and all affected projects.
- Creates git commits (unless `--no-commit` or `--skip commit`).
- Pushes commits (when `--push` is passed).

**Dependencies**:

- Requires the GitHub CLI (`gh`) for stage 3 (git-remote).
- Requires `conda` for stage 5 (conda).
- All repositories must have a clean working tree (no uncommitted changes).
