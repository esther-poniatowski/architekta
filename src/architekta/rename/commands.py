"""CLI command for cross-surface project renaming."""

from pathlib import Path
from typing import List, Optional

import typer

from architekta.diagnostics import DiagnosticEntry, DiagnosticLevel, emit
from architekta.infrastructure import GithubSlug, parse_github_remote
from architekta.rename.render import render_dry_run
from architekta.rename.pipeline import RenameError, run_rename_pipeline

app = typer.Typer(
    name="rename",
    help="Rename a project across all surfaces (filesystem, GitHub, conda, files).",
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
def rename(
    ctx: typer.Context,
    old_name: Optional[str] = typer.Argument(
        None, help="Current project name."
    ),
    new_name: Optional[str] = typer.Argument(
        None, help="New project name."
    ),
    path: Path = typer.Option(
        ".", "--path", help="Path to the project directory (default: current directory)."
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
    workspace: Optional[str] = typer.Option(
        None, "--workspace", help="VS Code workspace filename.",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show the full plan without applying any changes."
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
    if ctx.invoked_subcommand is not None:
        return

    if not old_name or not new_name:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=1)

    project_path = Path(path).resolve()

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
            affected_paths=tuple(affected_path or []),
            aliases=tuple(alias or []),
            github_slug=github_slug,
            conda_env=conda_env,
            workspace=workspace,
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
