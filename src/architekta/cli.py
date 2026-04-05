"""
Command-line interface for the `architekta` package.

Defines commands available via `python -m architekta` or `architekta` if installed as a script.

Commands
--------
info : Display diagnostic information.

See Also
--------
typer.Typer
    Library for building CLI applications: https://typer.tiangolo.com/
"""

import typer
from . import info, __version__
from .env.commands import app as env_app
from .github.commands import app as github_app
from .rename.commands import app as rename_app


# --- Main application instance --------------------------------------------------------------------

app = typer.Typer(add_completion=False, no_args_is_help=True)


# --- Global Commands ------------------------------------------------------------------------------


@app.command("info")
def cli_info() -> None:
    """Display version and platform diagnostics."""
    typer.echo(info())


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False, "--version", "-v", help="Show the package version and exit."
    )
) -> None:
    """Root command for the package command-line interface."""
    if version:
        typer.echo(__version__)
        raise typer.Exit()


# --- Commands for Environment Management ----------------------------------------------------------

app.add_typer(env_app, name="env")

# --- Commands for GitHub Repository Management -------------------------------------------------------

app.add_typer(github_app, name="github")

# --- Cross-surface Project Rename -----------------------------------------------------------------

app.add_typer(rename_app, name="rename")
