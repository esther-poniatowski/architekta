"""CLI commands for GitHub repository management."""

from pathlib import Path
from typing import List, Optional

import typer

from architekta.github.operations import discover_sibling_projects, sync_descriptions as execute_sync_descriptions

app = typer.Typer(name="github", help="GitHub repository management commands.")


@app.command(name="sync-descriptions", help="Synchronize GitHub repo descriptions with README first sentences.")
def sync_descriptions(
    projects: Optional[List[Path]] = typer.Argument(
        None, help="Paths to project directories. Defaults to sibling directories of the current project."
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying them."),
) -> None:
    if projects:
        dirs = [p.resolve() for p in projects]
    else:
        dirs = discover_sibling_projects(Path.cwd())

    if not dirs:
        typer.echo("[WARN] No project directories found.", err=True)
        raise typer.Exit(code=1)

    result = execute_sync_descriptions(dirs, dry_run=dry_run)
    for entry in result.targets:
        if entry.target == "readme":
            typer.echo(f"[SKIP] {entry.project_name}: {entry.message}", err=True)
            continue
        if entry.outcome == "ok":
            typer.echo(f"[OK]   {entry.project_name} [{entry.target}]: {entry.message}", err=True)
        elif entry.outcome == "dry-run":
            typer.echo(f"[DRY]  {entry.project_name} [{entry.target}]: {entry.message}", err=True)
        elif entry.outcome == "updated":
            typer.echo(f"[SET]  {entry.project_name} [{entry.target}]: {entry.message}", err=True)
        elif entry.outcome == "error":
            typer.echo(f"[ERR]  {entry.project_name} [{entry.target}]: {entry.message}", err=True)
        else:
            typer.echo(f"[SKIP] {entry.project_name} [{entry.target}]: {entry.message}", err=True)

    if result.has_failures:
        raise typer.Exit(code=1)
