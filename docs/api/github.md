<a id="github"></a>

# GitHub

GitHub repository management subcommands and supporting operations.

<a id="module-architekta.github.commands"></a>

<a id="commands"></a>

## Commands

CLI commands for GitHub repository management.

<a id="architekta.github.commands.sync_descriptions"></a>

### architekta.github.commands.sync_descriptions(projects=<typer.models.ArgumentInfo object>, dry_run=<typer.models.OptionInfo object>)

<a id="module-architekta.github.operations"></a>

<a id="operations"></a>

## Operations

Application-layer orchestration for GitHub synchronization.

<a id="architekta.github.operations.SyncTargetResult"></a>

### *class* architekta.github.operations.SyncTargetResult(project_name, target, current, desired, outcome, message, failed=False)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Outcome for synchronizing one metadata target of one project.

<a id="architekta.github.operations.SyncTargetResult.project_name"></a>

#### project_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.github.operations.SyncTargetResult.target"></a>

#### target *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.github.operations.SyncTargetResult.current"></a>

#### current *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)*

<a id="architekta.github.operations.SyncTargetResult.desired"></a>

#### desired *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)*

<a id="architekta.github.operations.SyncTargetResult.outcome"></a>

#### outcome *: [Literal](https://docs.python.org/3/library/typing.html#typing.Literal)['ok', 'dry-run', 'updated', 'skipped', 'error']*

<a id="architekta.github.operations.SyncTargetResult.message"></a>

#### message *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.github.operations.SyncTargetResult.failed"></a>

#### failed *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

<a id="architekta.github.operations.SyncBatchResult"></a>

### *class* architekta.github.operations.SyncBatchResult(targets)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Result of a batch metadata synchronization.

<a id="architekta.github.operations.SyncBatchResult.targets"></a>

#### targets *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[SyncTargetResult](#architekta.github.operations.SyncTargetResult), ...]*

<a id="architekta.github.operations.SyncBatchResult.has_failures"></a>

#### *property* has_failures *: [bool](https://docs.python.org/3/library/functions.html#bool)*

<a id="architekta.github.operations.TargetBinding"></a>

### *class* architekta.github.operations.TargetBinding(name, read_current, apply, missing_message=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Read and write behavior for one sync target.

<a id="architekta.github.operations.TargetBinding.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.github.operations.TargetBinding.read_current"></a>

#### read_current *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)], [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)]*

<a id="architekta.github.operations.TargetBinding.apply"></a>

#### apply *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path), [str](https://docs.python.org/3/library/stdtypes.html#str)], [None](https://docs.python.org/3/library/constants.html#None)]*

<a id="architekta.github.operations.TargetBinding.missing_message"></a>

#### missing_message *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

<a id="architekta.github.operations.discover_sibling_projects"></a>

### architekta.github.operations.discover_sibling_projects(cwd)

Return sibling directories of `cwd` that contain a README.md.

<a id="architekta.github.operations.sync_descriptions"></a>

### architekta.github.operations.sync_descriptions(dirs, \*, dry_run=False)

Synchronize project descriptions across configured metadata targets.

<a id="module-architekta.github.utils"></a>

<a id="utilities"></a>

## Utilities

Utility functions for GitHub repository metadata operations.

<a id="architekta.github.utils.extract_readme_description"></a>

### architekta.github.utils.extract_readme_description(project_dir)

Extract the first descriptive sentence from a project README.

Skips the title heading, badge lines, horizontal rules, HTML comments,
and blank lines, returning the first line of plain prose.

<a id="architekta.github.utils.get_github_remote"></a>

### architekta.github.utils.get_github_remote(project_dir)

Parse the origin remote URL to extract the GitHub owner and repo.

Returns a `GithubSlug` with `owner` and `repo` fields.

* **Raises:**
  [**RemoteNotFound**](#architekta.github.exceptions.RemoteNotFound) – If the git remote cannot be read or the URL is not a GitHub URL.

<a id="architekta.github.utils.get_current_description"></a>

### architekta.github.utils.get_current_description(owner, repo)

Fetch the current GitHub repository description via the gh CLI.

<a id="architekta.github.utils.set_description"></a>

### architekta.github.utils.set_description(owner, repo, description)

Update the GitHub repository description via the gh CLI.

<a id="architekta.github.utils.get_pyproject_description"></a>

### architekta.github.utils.get_pyproject_description(project_dir)

Read the description field from pyproject.toml, or None if absent.

<a id="architekta.github.utils.set_pyproject_description"></a>

### architekta.github.utils.set_pyproject_description(project_dir, description)

Update the description field in pyproject.toml in place.

<a id="module-architekta.github.exceptions"></a>

<a id="exceptions"></a>

## Exceptions

Exception hierarchy for GitHub operations.

<a id="architekta.github.exceptions.GitHubError"></a>

### *exception* architekta.github.exceptions.GitHubError(message, \*, diagnostics=None)

Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception)

<a id="architekta.github.exceptions.RemoteNotFound"></a>

### *exception* architekta.github.exceptions.RemoteNotFound(message, \*, diagnostics=None)

Bases: [`GitHubError`](#architekta.github.exceptions.GitHubError)

<a id="architekta.github.exceptions.DescriptionNotFound"></a>

### *exception* architekta.github.exceptions.DescriptionNotFound(message, \*, diagnostics=None)

Bases: [`GitHubError`](#architekta.github.exceptions.GitHubError)

<a id="architekta.github.exceptions.GhCliError"></a>

### *exception* architekta.github.exceptions.GhCliError(message, \*, diagnostics=None)

Bases: [`GitHubError`](#architekta.github.exceptions.GitHubError)

<a id="architekta.github.exceptions.MetadataParseError"></a>

### *exception* architekta.github.exceptions.MetadataParseError(message, \*, diagnostics=None)

Bases: [`GitHubError`](#architekta.github.exceptions.GitHubError)
