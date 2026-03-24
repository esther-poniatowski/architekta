"""CLI commands for GitHub repository management."""

from pathlib import Path
from typing import List, Optional

import typer

from architekta.github.exceptions import GitHubError
from architekta.github.utils import (
    extract_readme_description,
    get_github_remote,
    get_current_description,
    set_description,
    get_pyproject_description,
    set_pyproject_description,
)

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
        dirs = _discover_sibling_projects(Path.cwd())

    if not dirs:
        typer.echo("[WARN] No project directories found.", err=True)
        raise typer.Exit(code=1)

    errors = 0
    for project_dir in sorted(dirs):
        name = project_dir.name
        try:
            readme_desc = extract_readme_description(project_dir)
        except GitHubError as exc:
            typer.echo(f"[SKIP] {name}: {exc}", err=True)
            errors += 1
            continue

        # --- GitHub target ---
        try:
            owner, repo = get_github_remote(project_dir)
            current_gh = get_current_description(owner, repo)
        except GitHubError as exc:
            typer.echo(f"[SKIP] {name} [github]: {exc}", err=True)
            errors += 1
        else:
            if current_gh == readme_desc:
                typer.echo(f"[OK]   {name} [github]: already in sync", err=True)
            elif dry_run:
                typer.echo(f"[DRY]  {name} [github]: \"{current_gh}\" -> \"{readme_desc}\"", err=True)
            else:
                try:
                    set_description(owner, repo, readme_desc)
                    typer.echo(f"[SET]  {name} [github]: \"{readme_desc}\"", err=True)
                except GitHubError as exc:
                    typer.echo(f"[ERR]  {name} [github]: {exc}", err=True)
                    errors += 1

        # --- pyproject.toml target ---
        current_pp = get_pyproject_description(project_dir)
        if current_pp is None:
            typer.echo(f"[SKIP] {name} [pyproject]: no pyproject.toml or no description field", err=True)
        elif current_pp == readme_desc:
            typer.echo(f"[OK]   {name} [pyproject]: already in sync", err=True)
        elif dry_run:
            typer.echo(f"[DRY]  {name} [pyproject]: \"{current_pp}\" -> \"{readme_desc}\"", err=True)
        else:
            try:
                set_pyproject_description(project_dir, readme_desc)
                typer.echo(f"[SET]  {name} [pyproject]: \"{readme_desc}\"", err=True)
            except GitHubError as exc:
                typer.echo(f"[ERR]  {name} [pyproject]: {exc}", err=True)
                errors += 1

    if errors:
        raise typer.Exit(code=1)


def _discover_sibling_projects(cwd: Path) -> list[Path]:
    """Return sibling directories of ``cwd`` that contain a README.md."""
    parent = cwd.parent
    return [
        d
        for d in parent.iterdir()
        if d.is_dir() and d != cwd and (d / "README.md").exists() and (d / ".git").is_dir()
    ]
