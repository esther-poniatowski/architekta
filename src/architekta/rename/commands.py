"""CLI command for cross-surface project renaming."""

from pathlib import Path
from typing import List, Optional

import typer

from architekta.rename.plan import render_dry_run
from architekta.rename.pipeline import RenameError, run_rename_pipeline

app = typer.Typer(
    name="rename",
    help="Rename a project across all surfaces (filesystem, GitHub, conda, files).",
    no_args_is_help=True,
)

_DEFAULT_REGISTRY = Path("dev/registry.toml")


@app.callback(invoke_without_command=True)
def rename(
    ctx: typer.Context,
    old_name: Optional[str] = typer.Argument(
        None, help="Current canonical project name (registry key)."
    ),
    new_name: Optional[str] = typer.Argument(
        None, help="New canonical project name."
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
    registry: Path = typer.Option(
        _DEFAULT_REGISTRY,
        "--registry",
        help="Path to the registry TOML file.",
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

    try:
        report = run_rename_pipeline(
            old_name=old_name,
            new_name=new_name,
            registry_path=registry,
            dry_run=dry_run,
            push=push,
            skip_stages=set(skip) if skip else None,
            no_commit=no_commit,
            verbose=verbose,
        )
    except RenameError as exc:
        typer.echo(f"[ERR]  {exc}", err=True)
        raise typer.Exit(code=1)

    if dry_run:
        typer.echo(render_dry_run(report))
        return

    _print_report(report, verbose=verbose)

    if not report.succeeded:
        raise typer.Exit(code=1)


def _print_report(report: "object", *, verbose: bool) -> None:
    from architekta.rename.plan import PipelineReport, StageReport

    assert isinstance(report, PipelineReport)
    for stage in report.stages:
        assert isinstance(stage, StageReport)
        if stage.skipped:
            typer.echo(f"[SKIP] {stage.name}: {stage.skip_reason}", err=True)
        elif stage.error:
            typer.echo(f"[ERR]  {stage.name}: {stage.error}", err=True)
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
            typer.echo(f"[OK]   {stage.name}: {detail}", err=True)

            if verbose:
                for rename in stage.path_renames:
                    typer.echo(f"       mv {rename.old} → {rename.new}", err=True)
                for edit in stage.file_edits:
                    typer.echo(
                        f"       {edit.path}:{edit.line_number}  "
                        f"{edit.old_line!r} → {edit.new_line!r}",
                        err=True,
                    )
