"""CLI command for cross-surface project renaming.

The root of the project is resolved from ``--root``, then from the environment variable
``ARCHITEKTA_ROOT``, then from the current folder. Architekta has no settings file, so the command
does not search the ancestors of the current folder.

A rename changes the files of the researcher, so the command asks for a confirmation on a terminal.
``--yes`` answers it; without a terminal and without ``--yes``, the command stops with status 2.
``--dry-run`` needs no confirmation, since it changes nothing.
"""

import sys
from pathlib import Path
from typing import List, Optional

import typer

from architekta.diagnostics import DiagnosticEntry, DiagnosticLevel, emit
from architekta.infrastructure import GithubSlug, parse_github_remote
from architekta.rename.render import render_dry_run
from architekta.rename.pipeline import RenameError, run_rename_pipeline


def rename(
    old_name: str = typer.Argument(..., help="Current project name."),
    new_name: str = typer.Argument(..., help="New project name."),
    root: Path = typer.Option(
        ".",
        "--root",
        "-r",
        envvar="ARCHITEKTA_ROOT",
        help="Project folder to rename (default: ARCHITEKTA_ROOT, else the current folder).",
        file_okay=False,
    ),
    affected_path: Optional[List[Path]] = typer.Option(
        None,
        "--affected-path",
        help="Path to a project affected by the rename. Repeatable.",
    ),
    alias: Optional[List[str]] = typer.Option(
        None,
        "--alias",
        help="Former project name to also replace. Repeatable.",
    ),
    github_owner: Optional[str] = typer.Option(
        None, "--github-owner", help="GitHub owner (auto-detected from git remote).",
    ),
    conda_env: Optional[str] = typer.Option(
        None, "--conda-env", help="Current conda environment name.",
    ),
    workspace_file: Optional[str] = typer.Option(
        None, "--workspace-file", help="VS Code workspace filename.",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show the full plan without applying any changes."
    ),
    yes: bool = typer.Option(
        False, "--yes", help="Answer yes to the confirmation, for a run without a terminal."
    ),
    push: bool = typer.Option(
        False, "--push", help="Push commits in all affected repositories."
    ),
    skip: Optional[List[str]] = typer.Option(
        None,
        "--skip",
        help="Stage name to skip. Repeatable: --skip conda --skip commit.",
    ),
    no_commit: bool = typer.Option(
        False, "--no-commit", help="Execute all stages but skip the commit stage."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", help="Print each file modification as it occurs."
    ),
) -> None:
    """Rename a project across the filesystem, GitHub, conda, and all files."""
    project_path = Path(root).resolve()
    affected_paths = tuple(affected_path or [])

    if not dry_run:
        _confirm(old_name, new_name, project_path, affected_paths, yes=yes)

    # Resolve GitHub slug at the CLI layer.
    github_slug = parse_github_remote(project_path)
    if github_owner is not None:
        # Explicit owner overrides auto-detection.
        repo_name = github_slug.repo if github_slug else old_name
        github_slug = GithubSlug(owner=github_owner, repo=repo_name)

    try:
        report = run_rename_pipeline(
            old_name=old_name,
            new_name=new_name,
            project_path=project_path,
            affected_paths=affected_paths,
            aliases=tuple(alias or []),
            github_slug=github_slug,
            conda_env=conda_env,
            workspace=workspace_file,
            dry_run=dry_run,
            push=push,
            skip_stages=set(skip) if skip else None,
            no_commit=no_commit,
            verbose=verbose,
        )
    except RenameError as exc:
        emit(DiagnosticEntry(DiagnosticLevel.ERROR, "", str(exc)))
        raise typer.Exit(code=1)

    if dry_run:
        typer.echo(render_dry_run(report))
        return

    _print_report(report, verbose=verbose)

    if not report.succeeded:
        raise typer.Exit(code=1)


def _stdin_is_terminal() -> bool:
    """Return whether the standard input is a terminal that can answer a confirmation."""
    return sys.stdin.isatty()


def _confirm(
    old_name: str, new_name: str, project_path: Path, affected_paths: tuple[Path, ...], *, yes: bool,
) -> None:
    """Ask for the confirmation of a rename, or stop when no one can answer it.

    Raises
    ------
    typer.Exit
        With status 2 when the standard input is not a terminal and ``--yes`` is absent.
    click.exceptions.Abort
        When the researcher declines the confirmation; the command then exits with status 1.
    """
    if yes:
        return
    if not _stdin_is_terminal():
        emit(DiagnosticEntry(
            DiagnosticLevel.ERROR, "",
            "rename changes the files of the project and asks for a confirmation, but the standard "
            "input is not a terminal; give --yes to confirm, or --dry-run to preview the plan.",
        ))
        raise typer.Exit(code=2)
    scope = str(project_path)
    if affected_paths:
        scope += f" and {len(affected_paths)} affected project(s)"
    typer.confirm(
        f"Rename {old_name} to {new_name} in {scope}? This changes files, folders, the GitHub "
        "repository and the conda environment (preview with --dry-run).",
        default=False,
        abort=True,
    )


def _print_report(report: "object", *, verbose: bool) -> None:
    from architekta.rename.models import PipelineReport, StageReport

    assert isinstance(report, PipelineReport)
    for stage in report.stages:
        assert isinstance(stage, StageReport)
        if stage.skipped:
            emit(DiagnosticEntry(DiagnosticLevel.SKIP, stage.name, stage.skip_reason))
        elif stage.error:
            emit(DiagnosticEntry(DiagnosticLevel.ERROR, stage.name, stage.error))
        else:
            n_edits = len(stage.file_edits)
            n_files = len({e.path for e in stage.file_edits})
            n_cmds = len(stage.commands)
            summary = []
            if stage.path_renames:
                summary.append(f"{len(stage.path_renames)} rename(s)")
            if n_edits:
                summary.append(f"{n_edits} edit(s) in {n_files} file(s)")
            if n_cmds:
                summary.append(f"{n_cmds} command(s)")
            detail = ", ".join(summary) if summary else "no changes"
            emit(DiagnosticEntry(DiagnosticLevel.OK, stage.name, detail))

            if verbose:
                for rename_op in stage.path_renames:
                    typer.echo(f"       mv {rename_op.old} \u2192 {rename_op.new}", err=True)
                for edit in stage.file_edits:
                    typer.echo(
                        f"       {edit.path}:{edit.line_number}  "
                        f"{edit.old_line!r} \u2192 {edit.new_line!r}",
                        err=True,
                    )
