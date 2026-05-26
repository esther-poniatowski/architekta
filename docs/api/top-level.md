<a id="top-level"></a>

# Top-level

Top-level package entry points and shared infrastructure.

<a id="module-architekta"></a>

<a id="package"></a>

## Package

Initialization logic and public interface for the architekta package.

<a id="architekta.info"></a>

### architekta.info()

Format diagnostic information on package and platform.

<a id="module-architekta.cli"></a>

<a id="cli"></a>

## CLI

Command-line interface for the `architekta` package.

Defines commands available via `python -m architekta` or `architekta` if
installed as a script. Top-level commands:

- `info` — Display diagnostic information.

Subcommand groups are mounted on the root application from sibling packages:
`env` (environment management), `github` (repository management), and
`rename` (cross-surface project rename pipeline).

<a id="architekta.cli.cli_info"></a>

### architekta.cli.cli_info()

Display version and platform diagnostics.

<a id="architekta.cli.main_callback"></a>

### architekta.cli.main_callback(version=<typer.models.OptionInfo object>)

Root command for the package command-line interface.

<a id="module-architekta.diagnostics"></a>

<a id="diagnostics"></a>

## Diagnostics

Structured diagnostic output for CLI commands.

<a id="architekta.diagnostics.DiagnosticLevel"></a>

### *class* architekta.diagnostics.DiagnosticLevel(value, names=<not given>, \*values, module=None, qualname=None, type=None, start=1, boundary=None)

Bases: [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)

<a id="architekta.diagnostics.DiagnosticLevel.OK"></a>

#### OK *= 'OK'*

<a id="architekta.diagnostics.DiagnosticLevel.SKIP"></a>

#### SKIP *= 'SKIP'*

<a id="architekta.diagnostics.DiagnosticLevel.WARN"></a>

#### WARN *= 'WARN'*

<a id="architekta.diagnostics.DiagnosticLevel.ERROR"></a>

#### ERROR *= 'ERR'*

<a id="architekta.diagnostics.DiagnosticLevel.DRY"></a>

#### DRY *= 'DRY'*

<a id="architekta.diagnostics.DiagnosticLevel.SET"></a>

#### SET *= 'SET'*

<a id="architekta.diagnostics.DiagnosticEntry"></a>

### *class* architekta.diagnostics.DiagnosticEntry(level: 'DiagnosticLevel', context: 'str', message: 'str')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

<a id="architekta.diagnostics.DiagnosticEntry.level"></a>

#### level *: [DiagnosticLevel](#architekta.diagnostics.DiagnosticLevel)*

<a id="architekta.diagnostics.DiagnosticEntry.context"></a>

#### context *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.diagnostics.DiagnosticEntry.message"></a>

#### message *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.diagnostics.emit"></a>

### architekta.diagnostics.emit(entry)

<a id="module-architekta.infrastructure"></a>

<a id="infrastructure"></a>

## Infrastructure

Shared infrastructure utilities.

<a id="architekta.infrastructure.GitError"></a>

### *exception* architekta.infrastructure.GitError

Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception)

Raised when a git operation fails at the infrastructure layer.

<a id="architekta.infrastructure.CommandResult"></a>

### *class* architekta.infrastructure.CommandResult(args, returncode, stdout, stderr)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Structured subprocess result for infrastructure callers.

<a id="architekta.infrastructure.CommandResult.args"></a>

#### args *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]*

<a id="architekta.infrastructure.CommandResult.returncode"></a>

#### returncode *: [int](https://docs.python.org/3/library/functions.html#int)*

<a id="architekta.infrastructure.CommandResult.stdout"></a>

#### stdout *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.infrastructure.CommandResult.stderr"></a>

#### stderr *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.infrastructure.CommandResult.ok"></a>

#### *property* ok *: [bool](https://docs.python.org/3/library/functions.html#bool)*

<a id="architekta.infrastructure.run_command"></a>

### architekta.infrastructure.run_command(args, \*, cwd=None)

Run a subprocess command and preserve full diagnostics for the caller.

<a id="architekta.infrastructure.list_tracked_files"></a>

### architekta.infrastructure.list_tracked_files(repo_path)

Return all files tracked by git in a repository, excluding ignored files.

* **Raises:**
  [**GitError**](#architekta.infrastructure.GitError) – If the git command fails (e.g., not a git repo, git unavailable, bad path).
      Callers that want to tolerate unavailable repos must catch this explicitly.

<a id="architekta.infrastructure.is_text_file"></a>

### architekta.infrastructure.is_text_file(path)

Return True if the file can be decoded as UTF-8 text.

<a id="architekta.infrastructure.GithubSlug"></a>

### *class* architekta.infrastructure.GithubSlug(owner, repo)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A validated GitHub owner/repo identifier.

<a id="architekta.infrastructure.GithubSlug.owner"></a>

#### owner *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.infrastructure.GithubSlug.repo"></a>

#### repo *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.infrastructure.GithubSlug.from_url"></a>

#### *classmethod* from_url(url)

Extract owner/repo from a GitHub URL, or return `None`.

<a id="architekta.infrastructure.GithubSlug.ssh_url"></a>

#### *property* ssh_url *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Return the SSH clone URL for this repository.

<a id="architekta.infrastructure.parse_github_remote"></a>

### architekta.infrastructure.parse_github_remote(repo_path)

Read the origin remote URL and extract the GitHub owner/repo slug.

Returns `None` if the remote cannot be read or is not a GitHub URL.
