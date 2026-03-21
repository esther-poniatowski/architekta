""" """

from pathlib import Path
from typing import Optional, List
import typer
from architekta.env.utils import (
    get_site_packages,
    is_current_conda_env,
    is_base_conda_env,
    resolve_package_paths,
)


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
        if env is not None and not is_current_conda_env(env):
            typer.echo(f"[ERROR] Conda environment '{env}' is not active.", err=True)
            raise typer.Exit(code=4)

        if is_base_conda_env():
            typer.echo("[ERROR] Modifying the base Conda environment is not permitted.", err=True)
            raise typer.Exit(code=5)

        pkg_dirs = resolve_package_paths(packages, all, path)
        site_pkgs = get_site_packages()

        for pkg_name, pkg_dir in pkg_dirs.items():
            if not pkg_dir.exists():
                typer.echo(f"[ERROR] Package path not found: {pkg_dir}", err=True)
                raise typer.Exit(code=1)

            pth_file = site_pkgs / f"{pkg_name}.pth"
            lines = [str(pkg_dir.resolve())]

            if include_tests:
                test_path = pkg_dir.parent / "tests"
                if test_path.exists():
                    lines.append(str(test_path.resolve()))
                else:
                    typer.echo(
                        f"[WARN] Test directory not found for {pkg_name}: {test_path}", err=True
                    )

            if dry_run:
                typer.echo(
                    f"[DRY-RUN] Would write to {pth_file}:\n  " + "\n  ".join(lines), err=True
                )
                continue

            if not force and pth_file.exists():
                typer.echo(
                    f"[ERROR] .pth file already exists: {pth_file} (use --force to overwrite)",
                    err=True,
                )
                raise typer.Exit(code=3)

            pth_file.write_text("\n".join(lines))
            typer.echo(f"[OK] Installed {pkg_name} in editable mode: {pth_file}", err=True)

        raise typer.Exit(code=0)

    except ValueError as e:
        typer.echo(f"[ERROR] {e}", err=True)
        raise typer.Exit(code=2)
