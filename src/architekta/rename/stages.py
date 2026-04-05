"""Rename pipeline stage planners and the stage executor.

Each ``plan_*`` function is a pure planner: it accepts a ``RenameContext`` and
the accumulated ``PipelineReport`` from prior stages, inspects and reads the
filesystem, and returns a ``StagePlan`` describing what would be done.  No
write I/O is performed inside any planner.

``execute_stage_plan`` is the single execution entry point: it applies the
ordered steps from a ``StagePlan`` to the filesystem and runs any shell
commands.

There are 9 stages in total. Ordering constraints (load-bearing):
  2. Filesystem  -> before all others (renames the directory)
  3. Git remote  -> before Submodules (submodule URLs need the new remote)
  7. Cross-refs  -> before Submodules (source repo changes must be staged first)
  8. Submodules  -> after cross-refs
  9. Commit      -> last (all mutations must be complete)
"""

from pathlib import Path
from typing import Union

from architekta.infrastructure import GitError, is_text_file, list_tracked_files, run_command
from architekta.rename.context import RenameContext
from architekta.rename.models import (
    AffectedProject,
    CommandOutcome,
    FileEdit,
    FileProcessingResult,
    PathRename,
    PendingWrite,
    PipelineReport,
    ShellCommand,
    StagePlan,
    StageReport,
    STAGE_CROSS_REFS,
    STAGE_VALIDATE,
    STAGE_FILESYSTEM,
    STAGE_GIT_REMOTE,
    STAGE_WORKSPACES,
    STAGE_CONDA,
    STAGE_SELF_REFS,
    STAGE_SUBMODULES,
    STAGE_COMMIT,
)
from architekta.rename.patterns import PatternPair, apply_patterns_to_text


# ── Stage 1: Validate ─────────────────────────────────────────────────────────


def plan_validate(ctx: RenameContext, accumulated: PipelineReport) -> StagePlan:
    """Check all preconditions before any mutation occurs.

    Returns a StagePlan with an error if any precondition fails.
    The pipeline aborts planning of further stages when an error is present.
    Validate never produces execution steps.
    """
    errors: list[str] = []

    if not ctx.old_project_path.is_dir():
        errors.append(f"Source directory not found: {ctx.old_project_path}")
    if ctx.new_project_path.exists():
        errors.append(f"Target path already exists: {ctx.new_project_path}")

    for ap in ctx.affected_projects:
        if not ap.path.is_dir():
            errors.append(f"Affected project {ap.name!r} not found: {ap.path}")

    repos_to_check = [ctx.old_project_path] + [ap.path for ap in ctx.affected_projects]
    for repo_path in repos_to_check:
        if not repo_path.is_dir():
            continue
        result = run_command(["git", "-C", str(repo_path), "status", "--porcelain"])
        if result.ok and result.stdout:
            errors.append(
                f"Repository {repo_path} has uncommitted changes; "
                "commit or stash before renaming"
            )

    if errors:
        report = StageReport(
            stage_id=1,
            name=STAGE_VALIDATE,
            error="\n".join(errors),
        )
    else:
        report = StageReport(stage_id=1, name=STAGE_VALIDATE)

    return StagePlan(report=report, steps=())


# ── Stage 2: Filesystem ───────────────────────────────────────────────────────


def plan_filesystem(ctx: RenameContext, accumulated: PipelineReport) -> StagePlan:
    """Plan renaming the local project directory."""
    rename = PathRename(old=ctx.old_project_path, new=ctx.new_project_path)
    report = StageReport(
        stage_id=2,
        name=STAGE_FILESYSTEM,
        path_renames=(rename,),
    )
    return StagePlan(report=report, steps=(rename,))


# ── Stage 3: Git remote ───────────────────────────────────────────────────────


def plan_git_remote(ctx: RenameContext, accumulated: PipelineReport) -> StagePlan:
    """Plan renaming the GitHub repository and updating the local remote URL."""
    patch_cmd = ShellCommand(
        description="Rename GitHub repository",
        args=(
            "gh", "api", "-X", "PATCH",
            f"repos/{ctx.old_github}",
            "-f", f"name={ctx.new_name}",
        ),
    )
    new_url = ctx.new_github.ssh_url
    # cwd is new_project_path: this command runs after stage_filesystem renames
    # the directory, so the repo is at new_project_path at execution time.
    set_url_cmd = ShellCommand(
        description="Update local remote URL",
        args=("git", "remote", "set-url", "origin", new_url),
        cwd=ctx.new_project_path,
    )
    report = StageReport(
        stage_id=3,
        name=STAGE_GIT_REMOTE,
        commands=(patch_cmd, set_url_cmd),
    )
    return StagePlan(report=report, steps=(patch_cmd, set_url_cmd))


# ── Stage 4: Workspaces ───────────────────────────────────────────────────────


def plan_workspaces(ctx: RenameContext, accumulated: PipelineReport) -> StagePlan:
    """Plan updating VS Code workspace files that reference the project."""
    path_renames: list[PathRename] = []
    file_edits: list[FileEdit] = []
    steps: list[Union[PathRename, PendingWrite]] = []
    warnings: list[str] = []

    if ctx.old_workspace and ctx.new_workspace:
        # Candidates at their current (pre-rename) locations.
        workspace_candidates = [
            ctx.workspace_root / ctx.old_workspace,
            ctx.old_project_path / ctx.old_workspace,
        ]
        for ws_path in workspace_candidates:
            if ws_path.exists():
                # Files inside old_project_path will land at new_project_path.
                new_ws_path = (
                    _remap_to_new(ws_path.parent, ctx.old_project_path, ctx.new_project_path)
                    / ctx.new_workspace
                )
                rename = PathRename(old=ws_path, new=new_ws_path)
                path_renames.append(rename)
                steps.append(rename)

    # Scan all .code-workspace files under the workspace root.
    for ws_file in ctx.workspace_root.rglob("*.code-workspace"):
        if not is_text_file(ws_file):
            continue
        fpr = _collect_edits_and_write(ws_file, ctx.patterns, ctx)
        if fpr.error:
            warnings.append(fpr.error)
            continue
        if fpr.edits:
            file_edits.extend(fpr.edits)
            if fpr.pending_write is not None:
                steps.append(fpr.pending_write)

    report = StageReport(
        stage_id=4,
        name=STAGE_WORKSPACES,
        path_renames=tuple(path_renames),
        file_edits=tuple(file_edits),
        warnings=warnings,
    )
    return StagePlan(report=report, steps=tuple(steps))


# ── Stage 5: Conda environment ────────────────────────────────────────────────


def plan_conda(ctx: RenameContext, accumulated: PipelineReport) -> StagePlan:
    """Plan renaming the conda environment."""
    if not ctx.old_conda_env or not ctx.new_conda_env:
        report = StageReport(
            stage_id=5,
            name=STAGE_CONDA,
            skipped=True,
            skip_reason="no conda_env declared for this project",
        )
        return StagePlan(report=report, steps=())

    rename_cmd = ShellCommand(
        description="Rename conda environment",
        args=("conda", "rename", "-n", ctx.old_conda_env, ctx.new_conda_env, "--yes"),
    )
    report = StageReport(
        stage_id=5,
        name=STAGE_CONDA,
        commands=(rename_cmd,),
    )
    return StagePlan(report=report, steps=(rename_cmd,))


# ── Stage 6: Self-references ──────────────────────────────────────────────────


def plan_self_refs(ctx: RenameContext, accumulated: PipelineReport) -> StagePlan:
    """Plan replacing occurrences of the old name within the project's own files.

    Files are scanned at old_project_path (the current location during planning).
    PendingWrite targets are remapped to new_project_path, so the executor writes
    to the correct location after stage_filesystem has renamed the directory.
    """
    file_edits: list[FileEdit] = []
    steps: list[PendingWrite] = []
    warnings: list[str] = []

    try:
        tracked = list_tracked_files(ctx.old_project_path)
    except GitError as exc:
        report = StageReport(
            stage_id=6,
            name=STAGE_SELF_REFS,
            error=str(exc),
        )
        return StagePlan(report=report, steps=())

    for file_path in tracked:
        if not is_text_file(file_path):
            continue
        fpr = _collect_edits_and_write(file_path, ctx.patterns, ctx)
        if fpr.error:
            warnings.append(fpr.error)
            continue
        if fpr.edits:
            file_edits.extend(fpr.edits)
            if fpr.pending_write is not None:
                steps.append(fpr.pending_write)

    report = StageReport(
        stage_id=6,
        name=STAGE_SELF_REFS,
        file_edits=tuple(file_edits),
        warnings=warnings,
    )
    return StagePlan(report=report, steps=tuple(steps))


# ── Stage 7: Cross-references ─────────────────────────────────────────────────


def plan_cross_refs(ctx: RenameContext, accumulated: PipelineReport) -> StagePlan:
    """Plan replacing occurrences of the old name in all affected projects."""
    all_edits: list[FileEdit] = []
    steps: list[PendingWrite] = []
    errors: list[str] = []
    warnings: list[str] = []

    for ap in ctx.affected_projects:
        try:
            tracked = list_tracked_files(ap.path)
        except GitError as exc:
            errors.append(str(exc))
            continue
        for file_path in tracked:
            if not is_text_file(file_path):
                continue
            # Affected projects do not move; no remapping needed.
            fpr = _collect_edits_and_write(file_path, ctx.patterns, ctx)
            if fpr.error:
                warnings.append(fpr.error)
                continue
            if fpr.edits:
                all_edits.extend(fpr.edits)
                if fpr.pending_write is not None:
                    steps.append(fpr.pending_write)

    report = StageReport(
        stage_id=7,
        name=STAGE_CROSS_REFS,
        file_edits=tuple(all_edits),
        error="\n".join(errors) if errors else None,
        warnings=warnings,
    )
    return StagePlan(report=report, steps=tuple(steps))


# ── Stage 8: Submodules ───────────────────────────────────────────────────────


def plan_submodules(ctx: RenameContext, accumulated: PipelineReport) -> StagePlan:
    """Plan updating git submodule references involving the renamed project."""
    if not ctx.submodule_refs:
        report = StageReport(
            stage_id=8,
            name=STAGE_SUBMODULES,
            skipped=True,
            skip_reason="no git-submodule edges for this project",
        )
        return StagePlan(report=report, steps=())

    file_edits: list[FileEdit] = []
    steps: list[Union[PendingWrite, ShellCommand]] = []
    warnings: list[str] = []

    # Case A: Another project vendors the renamed project via .gitmodules.
    for ref in ctx.submodule_refs:
        gitmodules = ref.host_path / ".gitmodules"
        if gitmodules.exists():
            fpr = _collect_edits_and_write(gitmodules, ctx.patterns, ctx)
            if fpr.error:
                warnings.append(fpr.error)
            elif fpr.edits:
                file_edits.extend(fpr.edits)
                if fpr.pending_write is not None:
                    steps.append(fpr.pending_write)

        sync_cmd = ShellCommand(
            description=f"Sync submodules in {ref.host_name}",
            args=("git", "submodule", "sync"),
            cwd=ref.host_path,
        )
        steps.append(sync_cmd)

    # Case B: The renamed project itself hosts submodule(s) from affected projects.
    # After the filesystem rename, those submodule pointers need advancing.
    cross_refs_report = accumulated.find_stage(STAGE_CROSS_REFS)
    if cross_refs_report is not None:
        modified_paths = {e.path for e in cross_refs_report.file_edits}
        for ap in ctx.affected_projects:
            effective_path = _remap_to_new(ap.path, ctx.old_project_path, ctx.new_project_path)
            if any(p.is_relative_to(effective_path) for p in modified_paths):
                try:
                    relative_sub = effective_path.relative_to(ctx.new_project_path)
                except ValueError:
                    continue
                update_cmd = ShellCommand(
                    description=f"Update submodule pointer in {ctx.new_name} for {ap.name}",
                    args=(
                        "git", "submodule", "update", "--remote",
                        str(relative_sub),
                    ),
                    cwd=ctx.new_project_path,
                    checked=False,
                )
                steps.append(update_cmd)

    commands = tuple(s for s in steps if isinstance(s, ShellCommand))
    report = StageReport(
        stage_id=8,
        name=STAGE_SUBMODULES,
        file_edits=tuple(file_edits),
        commands=commands,
        warnings=warnings,
    )
    return StagePlan(report=report, steps=tuple(steps))


# ── Stage 9: Commit ───────────────────────────────────────────────────────────


def plan_commit(ctx: RenameContext, accumulated: PipelineReport) -> StagePlan:
    """Plan creating commits in all repositories that were modified."""
    commit_message = f"chore: rename {ctx.old_name} references to {ctx.new_name}"
    steps: list[ShellCommand] = []

    # Group modified files by their git repository root.
    repo_files: dict[Path, list[Path]] = {}
    for file_path in accumulated.all_modified_files:
        repo_root = _find_repo_root(file_path)
        if repo_root:
            repo_files.setdefault(repo_root, []).append(file_path)

    # Ensure the renamed repo itself is included even if no individual files
    # were recorded (the PathRename in stage_filesystem may be the only change).
    renamed_root = _find_repo_root(ctx.new_project_path)
    if renamed_root and renamed_root not in repo_files:
        repo_files[renamed_root] = []

    for repo_root, files in sorted(repo_files.items()):
        for file_path in files:
            steps.append(ShellCommand(
                description=f"Stage {file_path.name}",
                args=("git", "add", str(file_path)),
                cwd=repo_root,
                checked=False,
            ))

        steps.append(ShellCommand(
            description=f"Commit in {repo_root.name}",
            args=("git", "commit", "-m", commit_message),
            cwd=repo_root,
            checked=False,
        ))

        if ctx.push:
            steps.append(ShellCommand(
                description=f"Push {repo_root.name}",
                args=("git", "push"),
                cwd=repo_root,
                checked=True,
            ))

    report = StageReport(
        stage_id=9,
        name=STAGE_COMMIT,
        commands=tuple(steps),
    )
    return StagePlan(report=report, steps=tuple(steps))


# ── Executor ──────────────────────────────────────────────────────────────────


def execute_stage_plan(plan: StagePlan) -> list[CommandOutcome]:
    """Apply all execution steps in a stage plan in their declared order.

    This is the single execution entry point for all stages.  Called by the
    pipeline orchestrator once per stage (only in non-dry-run mode).

    Returns a list of ``CommandOutcome`` objects for any ``ShellCommand``
    steps (including unchecked commands that failed).
    """
    outcomes: list[CommandOutcome] = []
    for step in plan.steps:
        if isinstance(step, (PendingWrite, PathRename)):
            step.execute()
        elif isinstance(step, ShellCommand):
            result = step.execute()
            outcomes.append(CommandOutcome(
                args=result.args,
                returncode=result.returncode,
                ok=result.ok,
                error=result.stderr or result.stdout or "",
            ))
        else:
            raise TypeError(f"Unknown execution step type: {type(step).__name__}")
    return outcomes


# ── Private helpers ───────────────────────────────────────────────────────────


def _remap_to_new(path: Path, old_base: Path, new_base: Path) -> Path:
    """Return ``path`` remapped from ``old_base`` to ``new_base`` if it lives
    under ``old_base``; otherwise return ``path`` unchanged."""
    if path.is_relative_to(old_base):
        return new_base / path.relative_to(old_base)
    return path


def _collect_edits_and_write(
    file_path: Path,
    patterns: tuple[PatternPair, ...],
    ctx: RenameContext,
) -> FileProcessingResult:
    """Read a file, apply patterns, return line-level edits and a PendingWrite.

    The write target is remapped from ``old_project_path`` to
    ``new_project_path`` when ``file_path`` lives inside the renamed directory,
    so the executor writes to the correct post-rename location.

    Returns a ``FileProcessingResult`` with an error message on read failure,
    or empty edits when no patterns match.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        return FileProcessingResult(
            edits=[],
            pending_write=None,
            error=f"Cannot read {file_path}: {exc}",
        )

    lines = content.splitlines(keepends=True)
    write_path = _remap_to_new(file_path, ctx.old_project_path, ctx.new_project_path)
    edits: list[FileEdit] = []
    new_lines: list[str] = []

    for i, line in enumerate(lines, start=1):
        new_line, changed = apply_patterns_to_text(line, patterns)
        if changed:
            edits.append(FileEdit(
                path=write_path,
                line_number=i,
                old_line=line.rstrip("\n").rstrip("\r"),
                new_line=new_line.rstrip("\n").rstrip("\r"),
            ))
        new_lines.append(new_line)

    if not edits:
        return FileProcessingResult(edits=[], pending_write=None, error=None)

    return FileProcessingResult(
        edits=edits,
        pending_write=PendingWrite(path=write_path, content="".join(new_lines)),
        error=None,
    )


def _find_repo_root(path: Path) -> Path | None:
    """Return the nearest ancestor directory that contains a .git directory."""
    current = path if path.is_dir() else path.parent
    while current != current.parent:
        if (current / ".git").is_dir():
            return current
        current = current.parent
    return None
