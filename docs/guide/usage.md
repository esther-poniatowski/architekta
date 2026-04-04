# Usage

## Invocation

Architekta registers two entry points: `architekta` and the short alias `arkt`.
Both invoke the same CLI application.

```sh
architekta [COMMAND] [OPTIONS]
arkt [COMMAND] [OPTIONS]
```

The package can also run as a Python module:

```sh
python -m architekta [COMMAND] [OPTIONS]
```

## Global Options

`--version` / `-v` prints the installed version and exits:

```sh
architekta --version
```

`info` prints version, platform, and Python diagnostics:

```sh
architekta info
```

## Commands

### Installing Packages in Editable Mode

`env install-editable` creates `.pth` files in the active conda
environment's `site-packages` directory, adding package source directories to
the Python import path without building wheels or source distributions.

Install all packages found under `src/`:

```sh
architekta env install-editable --all
```

Install a single package by name (resolved relative to `src/`):

```sh
architekta env install-editable my_package
```

Install from an arbitrary directory:

```sh
architekta env install-editable --path ./libs/my_package
```

Preview the paths that would be written without modifying the environment:

```sh
architekta env install-editable --all --dry-run
```

Target a conda environment other than the currently active one:

```sh
architekta env install-editable --all --env myenv
```

Overwrite an existing `.pth` file (skipped by default):

```sh
architekta env install-editable my_package --force
```

Include the `tests/` directory alongside the package in the `.pth` file:

```sh
architekta env install-editable my_package --include-tests
```

### Synchronizing GitHub Descriptions

`github sync-descriptions` extracts the first prose sentence from
each project's `README.md` and propagates the description to two targets: the
GitHub repository description and the `description` field in `pyproject.toml`.

Synchronize all sibling project directories:

```sh
architekta github sync-descriptions
```

Preview changes without applying them:

```sh
architekta github sync-descriptions --dry-run
```

Synchronize specific project directories:

```sh
architekta github sync-descriptions ./project-a ./project-b
```

### Renaming a Project

`rename` propagates a name change across filesystem, GitHub, conda,
VS Code workspaces, submodules, and in-file references through a nine-stage
pipeline. All stages plan before executing, and `--dry-run` previews the full
plan without applying any mutation.

Preview a rename:

```sh
architekta rename old-name new-name --dry-run
```

Execute the rename from a specific project directory:

```sh
architekta rename old-name new-name --path /path/to/project
```

Propagate cross-references into sibling projects affected by the rename:

```sh
architekta rename old-name new-name \
  --affected-path ../sibling-a \
  --affected-path ../sibling-b
```

Replace former names alongside the current one:

```sh
architekta rename old-name new-name --alias former-name
```

Override the auto-detected GitHub owner:

```sh
architekta rename old-name new-name --github-owner my-org
```

Specify the conda environment name (when different from the project name):

```sh
architekta rename old-name new-name --conda-env old-name-dev
```

Rename the VS Code workspace file along with the project:

```sh
architekta rename old-name new-name --workspace old-name.code-workspace
```

Skip the conda environment rename stage:

```sh
architekta rename old-name new-name --skip conda
```

Rename without creating commits:

```sh
architekta rename old-name new-name --no-commit
```

Rename, commit, and push in one invocation:

```sh
architekta rename old-name new-name --push
```

Print each file modification during execution:

```sh
architekta rename old-name new-name --verbose
```

## Application Programming Interface

The same operations can be called as library functions.

```python
from architekta import info

print(info())
# architekta 0.0.0 | Platform: Darwin Python 3.12.8
```

Plan an editable install without writing to disk:

```python
from pathlib import Path

from architekta.env.operations import EditableInstallRequest, plan_editable_install
from architekta.env.utils import get_site_packages

request = EditableInstallRequest(
    workspace_root=Path.cwd(),
    site_packages=get_site_packages(),
    package_names=("my_package",),
    use_all=False,
    custom_path=None,
    include_tests=False,
    force=False,
)
result = plan_editable_install(request)

for plan in result.plans:
    print(plan.pth_file, plan.lines)
```

## Next Steps

- [CLI Reference](cli-reference.md) -- Full option and exit code documentation.
- [Configuration](configuration.md) -- Environment variables and tool configuration.
