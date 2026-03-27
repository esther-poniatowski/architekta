"""CLI commands for project registry management."""

from pathlib import Path
from typing import Optional

import typer

from architekta.registry.audit import find_stale_references
from architekta.registry.render import (
    render_dependencies_markdown,
    render_dependents_yaml,
    render_projects_markdown,
)
from architekta.registry.schema import load_registry
from architekta.registry.validation import validate_registry

app = typer.Typer(name="registry", help="Project registry management commands.")

_DEFAULT_REGISTRY = Path("dev/registry.toml")


@app.command("validate")
def validate_cmd(
    registry: Path = typer.Option(
        _DEFAULT_REGISTRY,
        "--registry",
        help="Path to the registry TOML file.",
    ),
    no_check_paths: bool = typer.Option(
        False, "--no-check-paths", help="Skip filesystem path existence checks."
    ),
) -> None:
    """Validate the registry for structural consistency."""
    reg = _load_or_exit(registry)
    result = validate_registry(reg, check_paths=not no_check_paths)

    for issue in result.issues:
        prefix = "[ERR] " if issue.severity == "error" else "[WARN]"
        typer.echo(f"{prefix} {issue.message}", err=True)

    if result.is_valid:
        typer.echo(
            f"[OK]  Registry valid: {len(reg.projects)} projects, "
            f"{len(reg.dependencies)} edges.",
            err=True,
        )
    else:
        typer.echo(
            f"[ERR] Registry invalid: {len(result.errors)} error(s).", err=True
        )
        raise typer.Exit(code=1)


@app.command("render")
def render_cmd(
    registry: Path = typer.Option(
        _DEFAULT_REGISTRY,
        "--registry",
        help="Path to the registry TOML file.",
    ),
    projects: bool = typer.Option(False, "--projects", help="Render the projects table."),
    dependencies: bool = typer.Option(
        False, "--dependencies", help="Render the dependencies table."
    ),
    dependents: Optional[str] = typer.Option(
        None,
        "--dependents",
        metavar="PROJECT",
        help="Render a YAML list of dependents for PROJECT.",
    ),
) -> None:
    """Regenerate derived artifacts from the registry."""
    if not any([projects, dependencies, dependents]):
        typer.echo("[WARN] Specify --projects, --dependencies, or --dependents.", err=True)
        raise typer.Exit(code=1)

    reg = _load_or_exit(registry)

    if projects:
        typer.echo(render_projects_markdown(reg))
    if dependencies:
        typer.echo(render_dependencies_markdown(reg))
    if dependents:
        typer.echo(render_dependents_yaml(reg, dependents))


@app.command("audit")
def audit_cmd(
    registry: Path = typer.Option(
        _DEFAULT_REGISTRY,
        "--registry",
        help="Path to the registry TOML file.",
    ),
) -> None:
    """Scan all tracked files for stale aliases from the registry."""
    reg = _load_or_exit(registry)
    references = find_stale_references(reg)

    if not references:
        typer.echo("[OK]  No stale references found.", err=True)
        return

    for ref in references:
        typer.echo(
            f"[STALE] {ref.file}:{ref.line_number}  "
            f"alias={ref.alias!r} (canonical: {ref.canonical_name!r})",
            err=True,
        )
    typer.echo(f"[WARN] {len(references)} stale reference(s) found.", err=True)
    raise typer.Exit(code=1)


def _load_or_exit(registry_path: Path) -> "object":
    from architekta.registry.exceptions import RegistryError

    try:
        return load_registry(registry_path)
    except RegistryError as exc:
        typer.echo(f"[ERR]  {exc}", err=True)
        raise typer.Exit(code=1)
