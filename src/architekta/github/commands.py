"""CLI commands for GitHub repository management."""

from pathlib import Path
from typing import List, Optional

import typer

from architekta.diagnostics import DiagnosticEntry, DiagnosticLevel, emit
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
        emit(DiagnosticEntry(DiagnosticLevel.WARN, "", "No project directories found."))
        raise typer.Exit(code=1)

    result = execute_sync_descriptions(dirs, dry_run=dry_run)

    _OUTCOME_TO_LEVEL = {
        "ok": DiagnosticLevel.OK,
        "dry-run": DiagnosticLevel.DRY,
        "updated": DiagnosticLevel.SET,
        "error": DiagnosticLevel.ERROR,
        "skipped": DiagnosticLevel.SKIP,
    }

    for entry in result.targets:
        if entry.target == "readme":
            emit(DiagnosticEntry(
                DiagnosticLevel.SKIP, entry.project_name, entry.message,
            ))
            continue
        context = f"{entry.project_name} [{entry.target}]"
        level = _OUTCOME_TO_LEVEL.get(entry.outcome, DiagnosticLevel.SKIP)
        emit(DiagnosticEntry(level, context, entry.message))

    if result.has_failures:
        raise typer.Exit(code=1)
