<a id="rename"></a>

# Rename

Cross-surface project rename pipeline.

<a id="module-architekta.rename.commands"></a>

<a id="commands"></a>

## Commands

CLI command for cross-surface project renaming.

<a id="architekta.rename.commands.rename"></a>

### architekta.rename.commands.rename(ctx, old_name=<typer.models.ArgumentInfo object>, new_name=<typer.models.ArgumentInfo object>, path=<typer.models.OptionInfo object>, affected_path=<typer.models.OptionInfo object>, alias=<typer.models.OptionInfo object>, github_owner=<typer.models.OptionInfo object>, conda_env=<typer.models.OptionInfo object>, workspace=<typer.models.OptionInfo object>, dry_run=<typer.models.OptionInfo object>, push=<typer.models.OptionInfo object>, skip=<typer.models.OptionInfo object>, no_commit=<typer.models.OptionInfo object>, verbose=<typer.models.OptionInfo object>)

Rename a project across the filesystem, GitHub, conda, and all files.

<a id="module-architekta.rename.models"></a>

<a id="models"></a>

## Models

Domain models for the rename pipeline: value objects, reports, and type aliases.

<a id="architekta.rename.models.Surface"></a>

### *class* architekta.rename.models.Surface(value, names=<not given>, \*values, module=None, qualname=None, type=None, start=1, boundary=None)

Bases: [`str`](https://docs.python.org/3/library/stdtypes.html#str), [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)

A location where a project’s name is encoded.

The rename pipeline must update every surface where the old name appears.
Surfaces are an enumerated classification: each stage targets one or more
surfaces, and the union of all covered surfaces defines the pipeline’s
completeness guarantee.

<a id="architekta.rename.models.Surface.FILESYSTEM"></a>

#### FILESYSTEM *= 'filesystem'*

<a id="architekta.rename.models.Surface.GITHUB"></a>

#### GITHUB *= 'github'*

<a id="architekta.rename.models.Surface.VSCODE_WORKSPACE"></a>

#### VSCODE_WORKSPACE *= 'vscode'*

<a id="architekta.rename.models.Surface.CONDA"></a>

#### CONDA *= 'conda'*

<a id="architekta.rename.models.Surface.SELF_REFERENCES"></a>

#### SELF_REFERENCES *= 'self-refs'*

<a id="architekta.rename.models.Surface.CROSS_REFERENCES"></a>

#### CROSS_REFERENCES *= 'cross-refs'*

<a id="architekta.rename.models.Surface.SUBMODULES"></a>

#### SUBMODULES *= 'submodules'*

<a id="architekta.rename.models.Surface.GIT"></a>

#### GIT *= 'git'*

<a id="architekta.rename.models.ProjectIdentity"></a>

### *class* architekta.rename.models.ProjectIdentity(name, path, github, conda_env=None, workspace=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

The identifying attributes of a project across all surfaces.

This is the central domain entity of the rename pipeline. It captures
everything about a project that may be encoded in another location and
therefore must be updated during a rename. It exists in two instances
within a `RenameContext`: one for the pre-rename state (`old`) and
one for the post-rename state (`new`).

<a id="architekta.rename.models.ProjectIdentity.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.models.ProjectIdentity.path"></a>

#### path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.rename.models.ProjectIdentity.github"></a>

#### github *: [GithubSlug](top-level.md#architekta.infrastructure.GithubSlug)*

<a id="architekta.rename.models.ProjectIdentity.conda_env"></a>

#### conda_env *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

<a id="architekta.rename.models.ProjectIdentity.workspace"></a>

#### workspace *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

<a id="architekta.rename.models.FileEdit"></a>

### *class* architekta.rename.models.FileEdit(path, line_number, old_line, new_line)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A single changed line produced by a pattern replacement.

<a id="architekta.rename.models.FileEdit.path"></a>

#### path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.rename.models.FileEdit.line_number"></a>

#### line_number *: [int](https://docs.python.org/3/library/functions.html#int)*

<a id="architekta.rename.models.FileEdit.old_line"></a>

#### old_line *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.models.FileEdit.new_line"></a>

#### new_line *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.models.PathRename"></a>

### *class* architekta.rename.models.PathRename(old, new)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A filesystem path rename (directory or file).

<a id="architekta.rename.models.PathRename.old"></a>

#### old *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.rename.models.PathRename.new"></a>

#### new *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.rename.models.PathRename.execute"></a>

#### execute()

Apply the rename to the filesystem.

<a id="architekta.rename.models.ShellCommand"></a>

### *class* architekta.rename.models.ShellCommand(description, args, cwd=None, checked=True)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A subprocess command run (or planned) by a pipeline stage.

When `checked` is True the executor raises on non-zero exit; when False
the command is run best-effort (e.g. `git commit` which exits non-zero
when there is nothing to commit).

<a id="architekta.rename.models.ShellCommand.description"></a>

#### description *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.models.ShellCommand.args"></a>

#### args *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]*

<a id="architekta.rename.models.ShellCommand.cwd"></a>

#### cwd *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

<a id="architekta.rename.models.ShellCommand.checked"></a>

#### checked *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= True*

<a id="architekta.rename.models.ShellCommand.execute"></a>

#### execute()

Run the command and return the result.

* **Raises:**
  [**RuntimeError**](https://docs.python.org/3/library/exceptions.html#RuntimeError) – If the command is `checked` and exits with a non-zero code.

<a id="architekta.rename.models.PendingWrite"></a>

### *class* architekta.rename.models.PendingWrite(path, content)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Full file content to write during the execution phase.

<a id="architekta.rename.models.PendingWrite.path"></a>

#### path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.rename.models.PendingWrite.content"></a>

#### content *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.models.PendingWrite.execute"></a>

#### execute()

Write the content to the target path.

<a id="architekta.rename.models.CommandOutcome"></a>

### *class* architekta.rename.models.CommandOutcome(args, returncode, ok, error)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Structured outcome of a shell command execution.

<a id="architekta.rename.models.CommandOutcome.args"></a>

#### args *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]*

<a id="architekta.rename.models.CommandOutcome.returncode"></a>

#### returncode *: [int](https://docs.python.org/3/library/functions.html#int)*

<a id="architekta.rename.models.CommandOutcome.ok"></a>

#### ok *: [bool](https://docs.python.org/3/library/functions.html#bool)*

<a id="architekta.rename.models.CommandOutcome.error"></a>

#### error *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.models.FileProcessingResult"></a>

### *class* architekta.rename.models.FileProcessingResult(edits, pending_write, error)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Result of reading a file, applying patterns, and preparing a write.

<a id="architekta.rename.models.FileProcessingResult.edits"></a>

#### edits *: [list](https://docs.python.org/3/library/stdtypes.html#list)[[FileEdit](#architekta.rename.models.FileEdit)]*

<a id="architekta.rename.models.FileProcessingResult.pending_write"></a>

#### pending_write *: [PendingWrite](#architekta.rename.models.PendingWrite) | [None](https://docs.python.org/3/library/constants.html#None)*

<a id="architekta.rename.models.FileProcessingResult.error"></a>

#### error *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)*

<a id="architekta.rename.models.StageReport"></a>

### *class* architekta.rename.models.StageReport(stage_id, name, path_renames=(), file_edits=(), commands=(), skipped=False, skip_reason='', error=None, description='', warnings=<factory>)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Output of one pipeline stage (actual or planned in dry-run mode).

<a id="architekta.rename.models.StageReport.stage_id"></a>

#### stage_id *: [int](https://docs.python.org/3/library/functions.html#int)*

<a id="architekta.rename.models.StageReport.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.models.StageReport.path_renames"></a>

#### path_renames *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[PathRename](#architekta.rename.models.PathRename), ...]* *= ()*

<a id="architekta.rename.models.StageReport.file_edits"></a>

#### file_edits *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[FileEdit](#architekta.rename.models.FileEdit), ...]* *= ()*

<a id="architekta.rename.models.StageReport.commands"></a>

#### commands *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[ShellCommand](#architekta.rename.models.ShellCommand), ...]* *= ()*

<a id="architekta.rename.models.StageReport.skipped"></a>

#### skipped *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

<a id="architekta.rename.models.StageReport.skip_reason"></a>

#### skip_reason *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

<a id="architekta.rename.models.StageReport.error"></a>

#### error *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

<a id="architekta.rename.models.StageReport.description"></a>

#### description *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

<a id="architekta.rename.models.StageReport.warnings"></a>

#### warnings *: [list](https://docs.python.org/3/library/stdtypes.html#list)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

<a id="architekta.rename.models.StageReport.succeeded"></a>

#### *property* succeeded *: [bool](https://docs.python.org/3/library/functions.html#bool)*

<a id="architekta.rename.models.StageReport.modified_files"></a>

#### *property* modified_files *: [frozenset](https://docs.python.org/3/library/stdtypes.html#frozenset)[[Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)]*

<a id="architekta.rename.models.StagePlan"></a>

### *class* architekta.rename.models.StagePlan(report, steps)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Planner output: a public StageReport plus an ordered execution sequence.

`report` is the display model (used for dry-run output and logging).
`steps` is the ordered list of I/O actions to apply during execution.
The two are kept separate so that planning is always side-effect-free and
execution is driven entirely from the `steps` sequence without re-reading
any files.

<a id="architekta.rename.models.StagePlan.report"></a>

#### report *: [StageReport](#architekta.rename.models.StageReport)*

<a id="architekta.rename.models.StagePlan.steps"></a>

#### steps *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[PendingWrite](#architekta.rename.models.PendingWrite) | [PathRename](#architekta.rename.models.PathRename) | [ShellCommand](#architekta.rename.models.ShellCommand), ...]*

<a id="architekta.rename.models.PipelineReport"></a>

### *class* architekta.rename.models.PipelineReport(old_name, new_name, dry_run, stages)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Aggregate result of a complete rename pipeline run.

<a id="architekta.rename.models.PipelineReport.old_name"></a>

#### old_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.models.PipelineReport.new_name"></a>

#### new_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.models.PipelineReport.dry_run"></a>

#### dry_run *: [bool](https://docs.python.org/3/library/functions.html#bool)*

<a id="architekta.rename.models.PipelineReport.stages"></a>

#### stages *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[StageReport](#architekta.rename.models.StageReport), ...]*

<a id="architekta.rename.models.PipelineReport.succeeded"></a>

#### *property* succeeded *: [bool](https://docs.python.org/3/library/functions.html#bool)*

<a id="architekta.rename.models.PipelineReport.all_modified_files"></a>

#### *property* all_modified_files *: [frozenset](https://docs.python.org/3/library/stdtypes.html#frozenset)[[Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)]*

<a id="architekta.rename.models.PipelineReport.find_stage"></a>

#### find_stage(name)

Return the StageReport for the given stage name, or None.

<a id="architekta.rename.models.AffectedProject"></a>

### *class* architekta.rename.models.AffectedProject(name, path)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A project with a dependency edge to or from the renamed project.

<a id="architekta.rename.models.AffectedProject.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.models.AffectedProject.path"></a>

#### path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.rename.models.SubmoduleRef"></a>

### *class* architekta.rename.models.SubmoduleRef(host_name, host_path, old_submodule_url, new_submodule_url)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A git-submodule edge involving the renamed project.

<a id="architekta.rename.models.SubmoduleRef.host_name"></a>

#### host_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.models.SubmoduleRef.host_path"></a>

#### host_path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.rename.models.SubmoduleRef.old_submodule_url"></a>

#### old_submodule_url *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.models.SubmoduleRef.new_submodule_url"></a>

#### new_submodule_url *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="module-architekta.rename.patterns"></a>

<a id="patterns"></a>

## Patterns

Name pattern generation and text replacement for rename operations.

<a id="architekta.rename.patterns.PatternPair"></a>

### *class* architekta.rename.patterns.PatternPair(search, replace)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A single search-replace pair used during a rename.

<a id="architekta.rename.patterns.PatternPair.search"></a>

#### search *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.patterns.PatternPair.replace"></a>

#### replace *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.patterns.generate_patterns"></a>

### architekta.rename.patterns.generate_patterns(old_name, new_name, old_aliases, old_abs_path, new_abs_path, old_conda_env=None, new_conda_env=None)

Generate ordered (search, replace) pattern pairs for a project rename.

Patterns are sorted longest-first so that more specific forms (e.g., full
path, conda env name with suffix) are replaced before shorter ones (e.g.,
the bare project name), preventing partial-match corruption.

* **Parameters:**
  * **old_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – The canonical old project name.
  * **new_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – The canonical new project name.
  * **old_aliases** ([*list*](https://docs.python.org/3/library/stdtypes.html#list) *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Former names that should also be replaced.  Each alias maps to
    new_name.
  * **old_abs_path** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Absolute filesystem paths to the project directory.
  * **new_abs_path** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Absolute filesystem paths to the project directory.
  * **old_conda_env** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Conda environment names, if the project declares one. Only added when
    the conda env name differs from the project name (otherwise the direct
    name pattern already covers it).
  * **new_conda_env** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Conda environment names, if the project declares one. Only added when
    the conda env name differs from the project name (otherwise the direct
    name pattern already covers it).

<a id="architekta.rename.patterns.apply_patterns_to_text"></a>

### architekta.rename.patterns.apply_patterns_to_text(text, patterns)

Apply all patterns to a text string and indicate whether it changed.

Patterns are applied in the order given (caller is responsible for
longest-first ordering via `generate_patterns`).

<a id="module-architekta.rename.context"></a>

<a id="context"></a>

## Context

Rename context: immutable state assembled before pipeline execution.

<a id="architekta.rename.context.RenameContext"></a>

### *class* architekta.rename.context.RenameContext(old, new, patterns, affected_projects, submodule_refs, workspace_root, skip_stages, push)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

All computed state required by rename pipeline stages.

Built once before any stage runs.  Frozen so that stages cannot mutate
shared state.  Because planning and execution are separated, this context
always reflects the pre-rename state; stages derive execution paths
(e.g. `new.path`) from the stored fields.

The project’s identity is captured by two `ProjectIdentity`
instances — `old` (pre-rename) and `new` (post-rename) — separating
the domain concept “what the project is” from the pipeline configuration
“how to rename it”.

<a id="architekta.rename.context.RenameContext.old"></a>

#### old *: [ProjectIdentity](#architekta.rename.models.ProjectIdentity)*

<a id="architekta.rename.context.RenameContext.new"></a>

#### new *: [ProjectIdentity](#architekta.rename.models.ProjectIdentity)*

<a id="architekta.rename.context.RenameContext.patterns"></a>

#### patterns *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[PatternPair](#architekta.rename.patterns.PatternPair), ...]*

<a id="architekta.rename.context.RenameContext.affected_projects"></a>

#### affected_projects *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[AffectedProject](#architekta.rename.models.AffectedProject), ...]*

<a id="architekta.rename.context.RenameContext.submodule_refs"></a>

#### submodule_refs *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[SubmoduleRef](#architekta.rename.models.SubmoduleRef), ...]*

<a id="architekta.rename.context.RenameContext.workspace_root"></a>

#### workspace_root *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.rename.context.RenameContext.skip_stages"></a>

#### skip_stages *: [frozenset](https://docs.python.org/3/library/stdtypes.html#frozenset)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

<a id="architekta.rename.context.RenameContext.push"></a>

#### push *: [bool](https://docs.python.org/3/library/functions.html#bool)*

<a id="architekta.rename.context.RenameContext.old_name"></a>

#### *property* old_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.context.RenameContext.new_name"></a>

#### *property* new_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.context.RenameContext.old_project_path"></a>

#### *property* old_project_path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.rename.context.RenameContext.new_project_path"></a>

#### *property* new_project_path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

<a id="architekta.rename.context.RenameContext.old_github"></a>

#### *property* old_github *: [GithubSlug](top-level.md#architekta.infrastructure.GithubSlug)*

<a id="architekta.rename.context.RenameContext.new_github"></a>

#### *property* new_github *: [GithubSlug](top-level.md#architekta.infrastructure.GithubSlug)*

<a id="architekta.rename.context.RenameContext.old_conda_env"></a>

#### *property* old_conda_env *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)*

<a id="architekta.rename.context.RenameContext.new_conda_env"></a>

#### *property* new_conda_env *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)*

<a id="architekta.rename.context.RenameContext.old_workspace"></a>

#### *property* old_workspace *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)*

<a id="architekta.rename.context.RenameContext.new_workspace"></a>

#### *property* new_workspace *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)*

<a id="architekta.rename.context.build_rename_context"></a>

### architekta.rename.context.build_rename_context(old_name, new_name, project_path, \*, affected_paths=(), aliases=(), github_slug=None, conda_env=None, workspace=None, skip_stages=frozenset({}), push=False)

Build a frozen rename context from explicit parameters.

* **Parameters:**
  * **project_path** ([*Path*](https://docs.python.org/3/library/pathlib.html#pathlib.Path)) – Absolute path to the project directory being renamed.
  * **affected_paths** ([*tuple*](https://docs.python.org/3/library/stdtypes.html#tuple) *[*[*Path*](https://docs.python.org/3/library/pathlib.html#pathlib.Path) *,*  *...* *]*) – Paths to other projects whose files should be scanned for
    cross-references (e.g. sibling projects that depend on this one).
  * **aliases** ([*tuple*](https://docs.python.org/3/library/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,*  *...* *]*) – Former project names that should also be replaced during renaming.
  * **github_slug** ([*GithubSlug*](top-level.md#architekta.infrastructure.GithubSlug) *|* *None*) – Pre-resolved GitHub owner/repo slug.  When `None` the GitHub-related
    stages will operate without slug information (the caller is responsible
    for resolving it via `parse_github_remote` at the CLI layer).
  * **conda_env** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Current conda environment name, if distinct from the project name.
  * **workspace** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – VS Code workspace filename (e.g. `"myproject.code-workspace"`).

<a id="module-architekta.rename.plan"></a>

<a id="plan"></a>

## Plan

Domain models for the rename pipeline.

This module re-exports from the decomposed submodules for backward compatibility.

<a id="module-architekta.rename.stages"></a>

<a id="stages"></a>

## Stages

Rename pipeline stage planners and the stage executor.

Each `plan_*` function is a pure planner: it accepts a `RenameContext` and
the accumulated `PipelineReport` from prior stages, inspects and reads the
filesystem, and returns a `StagePlan` describing what would be done.  No
write I/O is performed inside any planner.

`execute_stage_plan` is the single execution entry point: it applies the
ordered steps from a `StagePlan` to the filesystem and runs any shell
commands.

There are 9 stages in total. Ordering constraints (load-bearing):

- Filesystem (stage 2) before all others; the directory rename must happen first.
- Git remote (stage 3) before Submodules; submodule URLs need the new remote.
- Cross-refs (stage 7) before Submodules; source repo changes must be staged first.
- Submodules (stage 8) after cross-refs.
- Commit (stage 9) last; all mutations must be complete.

<a id="architekta.rename.stages.plan_validate"></a>

### architekta.rename.stages.plan_validate(ctx, accumulated)

Check all preconditions before any mutation occurs.

Returns a StagePlan with an error if any precondition fails.
The pipeline aborts planning of further stages when an error is present.
Validate never produces execution steps.

<a id="architekta.rename.stages.plan_filesystem"></a>

### architekta.rename.stages.plan_filesystem(ctx, accumulated)

Plan renaming the local project directory.

<a id="architekta.rename.stages.plan_git_remote"></a>

### architekta.rename.stages.plan_git_remote(ctx, accumulated)

Plan renaming the GitHub repository and updating the local remote URL.

<a id="architekta.rename.stages.plan_workspaces"></a>

### architekta.rename.stages.plan_workspaces(ctx, accumulated)

Plan updating VS Code workspace files that reference the project.

<a id="architekta.rename.stages.plan_conda"></a>

### architekta.rename.stages.plan_conda(ctx, accumulated)

Plan renaming the conda environment.

<a id="architekta.rename.stages.plan_self_refs"></a>

### architekta.rename.stages.plan_self_refs(ctx, accumulated)

Plan replacing occurrences of the old name within the project’s own files.

Files are scanned at old_project_path (the current location during planning).
PendingWrite targets are remapped to new_project_path, so the executor writes
to the correct location after stage_filesystem has renamed the directory.

<a id="architekta.rename.stages.plan_cross_refs"></a>

### architekta.rename.stages.plan_cross_refs(ctx, accumulated)

Plan replacing occurrences of the old name in all affected projects.

<a id="architekta.rename.stages.plan_submodules"></a>

### architekta.rename.stages.plan_submodules(ctx, accumulated)

Plan updating git submodule references involving the renamed project.

<a id="architekta.rename.stages.plan_commit"></a>

### architekta.rename.stages.plan_commit(ctx, accumulated)

Plan creating commits in all repositories that were modified.

<a id="architekta.rename.stages.execute_stage_plan"></a>

### architekta.rename.stages.execute_stage_plan(plan)

Apply all execution steps in a stage plan in their declared order.

This is the single execution entry point for all stages.  Called by the
pipeline orchestrator once per stage (only in non-dry-run mode).

Returns a list of `CommandOutcome` objects for any `ShellCommand`
steps (including unchecked commands that failed).

<a id="module-architekta.rename.pipeline"></a>

<a id="pipeline"></a>

## Pipeline

Rename pipeline orchestration: stage registration, planning, and execution.

<a id="architekta.rename.pipeline.RenameError"></a>

### *exception* architekta.rename.pipeline.RenameError

Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception)

Raised when the rename pipeline cannot proceed.

<a id="architekta.rename.pipeline.StageDescriptor"></a>

### *class* architekta.rename.pipeline.StageDescriptor(stage_id, name, skippable, fn, depends_on=(), surfaces=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Metadata and planning function for one pipeline stage.

<a id="architekta.rename.pipeline.StageDescriptor.stage_id"></a>

#### stage_id *: [int](https://docs.python.org/3/library/functions.html#int)*

<a id="architekta.rename.pipeline.StageDescriptor.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="architekta.rename.pipeline.StageDescriptor.skippable"></a>

#### skippable *: [bool](https://docs.python.org/3/library/functions.html#bool)*

<a id="architekta.rename.pipeline.StageDescriptor.fn"></a>

#### fn *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[RenameContext](#architekta.rename.context.RenameContext), [PipelineReport](#architekta.rename.models.PipelineReport)], [StagePlan](#architekta.rename.models.StagePlan)]*

<a id="architekta.rename.pipeline.StageDescriptor.depends_on"></a>

#### depends_on *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

<a id="architekta.rename.pipeline.StageDescriptor.surfaces"></a>

#### surfaces *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[Surface](#architekta.rename.models.Surface), ...]* *= ()*

<a id="architekta.rename.pipeline.run_rename_pipeline"></a>

### architekta.rename.pipeline.run_rename_pipeline(old_name, new_name, \*, project_path, affected_paths=(), aliases=(), github_slug=None, conda_env=None, workspace=None, dry_run=False, push=False, skip_stages=None, no_commit=False, verbose=False)

Execute the full cross-surface project rename pipeline.

* **Parameters:**
  * **old_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Current and target project names.
  * **new_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Current and target project names.
  * **project_path** ([*Path*](https://docs.python.org/3/library/pathlib.html#pathlib.Path)) – Path to the project directory being renamed.
  * **affected_paths** ([*tuple*](https://docs.python.org/3/library/stdtypes.html#tuple) *[*[*Path*](https://docs.python.org/3/library/pathlib.html#pathlib.Path) *,*  *...* *]*) – Paths to other projects whose files should be scanned for
    cross-references to the old name.
  * **aliases** ([*tuple*](https://docs.python.org/3/library/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,*  *...* *]*) – Former project names that should also be replaced.
  * **github_slug** ([*GithubSlug*](top-level.md#architekta.infrastructure.GithubSlug) *|* *None*) – Pre-resolved GitHub owner/repo slug.  If `None`, the context builder
    will raise an error.  Resolve at the CLI layer via
    `parse_github_remote`.
  * **conda_env** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Current conda environment name, if distinct from the project name.
  * **workspace** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – VS Code workspace filename (e.g. `"myproject.code-workspace"`).
  * **dry_run** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If True, plan all stages but apply none.
  * **push** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If True, push commits in all affected repositories after commit stage.
  * **skip_stages** ([*set*](https://docs.python.org/3/library/stdtypes.html#set) *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*  *|* *None*) – Set of stage names to skip (must be skippable stages, e.g.
    `{"conda", "commit"}`).
  * **no_commit** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Convenience shorthand that adds `"commit"` to skip_stages.
  * **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Passed through to the caller for display; does not affect execution.
* **Returns:**
  Aggregate result of all stages. Check `report.succeeded` to
  determine whether any stage failed.
* **Return type:**
  [PipelineReport](#architekta.rename.models.PipelineReport)
* **Raises:**
  [**RenameError**](#architekta.rename.pipeline.RenameError) – If project parameters are invalid or Stage 1 (Validate) reports
      errors.

<a id="module-architekta.rename.render"></a>

<a id="rendering"></a>

## Rendering

Dry-run rendering for pipeline reports.

<a id="architekta.rename.render.render_dry_run"></a>

### architekta.rename.render.render_dry_run(report)

Format a pipeline report as a human-readable dry-run preview.
