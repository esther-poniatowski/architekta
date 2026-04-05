"""CLI commands for environment management."""

import os
from pathlib import Path
from typing import Optional, List

import typer

from architekta.diagnostics import DiagnosticEntry, DiagnosticLevel, emit
from architekta.env.exceptions import EnvError
from architekta.env.operations import EditableInstallRequest, execute_install_plans, plan_editable_install
from architekta.env.utils import get_site_packages


app = typer.Typer(name="env", help="Environment management commands for Architekta.")


@app.command(name="install-editable", help="Install packages in editable mode.")
def install_editable(
    packages: List[str] = typer.Argument(None, help="Name(s) of the package(s) to install."),
    all: bool = typer.Option(False, "--all", help="Install all packages in the src directory."),
    path: Optional[Path] = typer.Option(None, "--path", help="Path to a single package directory."),
    include_tests: bool = typer.Option(False, "--include-tests", help="Include test directory."),
    env: Optional[str] = typer.Option(None, "--env", help="Target conda environment name."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing .pth file if present."),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview installation paths without modifying environment."
    ),
) -> None:
    try:
        request = EditableInstallRequest(
            workspace_root=Path.cwd(),
            site_packages=get_site_packages(),
            package_names=tuple(packages or []),
            use_all=all,
            custom_path=path,
            include_tests=include_tests,
            force=force,
            active_env=os.environ.get("CONDA_DEFAULT_ENV"),
            conda_prefix=os.environ.get("CONDA_PREFIX"),
            target_env=env,
        )
        result = plan_editable_install(request)

        for plan in result.plans:
            if plan.skipped:
                emit(DiagnosticEntry(
                    DiagnosticLevel.ERROR, plan.package.name, plan.skip_reason,
                ))
                raise typer.Exit(code=3)

            if dry_run:
                emit(DiagnosticEntry(
                    DiagnosticLevel.DRY, plan.package.name,
                    f"Would write to {plan.pth_file}:\n  " + "\n  ".join(plan.lines),
                ))
                continue

        if not dry_run:
            execute_install_plans(result)
            for plan in result.plans:
                emit(DiagnosticEntry(
                    DiagnosticLevel.OK, plan.package.name,
                    f"Installed in editable mode: {plan.pth_file}",
                ))

        raise typer.Exit(code=0)

    except EnvError as e:
        emit(DiagnosticEntry(DiagnosticLevel.ERROR, "", str(e)))
        raise typer.Exit(code=2)
