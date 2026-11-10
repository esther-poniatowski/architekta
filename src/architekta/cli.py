"""Command-line interface for the ``architekta`` package.

Defines commands available via ``python -m architekta`` or ``architekta`` if
installed as a script. Top-level commands:

- ``info`` — Display diagnostic information.

Subcommand groups are mounted on the root application from sibling packages:
``env`` (environment management) and ``github`` (repository management). The command
``rename`` (cross-surface project rename pipeline) is a plain command, so that its options
may follow its positional names.
"""

import typer
from . import info, __version__
from .env.commands import app as env_app
from .github.commands import app as github_app
from .rename.commands import rename


# --- Main application instance --------------------------------------------------------------------

app = typer.Typer(add_completion=False, no_args_is_help=True)


# --- Global Commands ------------------------------------------------------------------------------


@app.command("info")
def cli_info() -> None:
    """Display version and platform diagnostics."""
    typer.echo(info())


def _print_version(value: bool) -> None:
    """Print the package version and exit, before any command is required."""
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=_print_version,
        is_eager=True,
        help="Show the package version and exit.",
    )
) -> None:
    """Root command for the package command-line interface."""


# --- Commands for Environment Management ----------------------------------------------------------

app.add_typer(env_app, name="env")

# --- Commands for GitHub Repository Management -------------------------------------------------------

app.add_typer(github_app, name="github")

# --- Cross-surface Project Rename -----------------------------------------------------------------

app.command(
    "rename", help="Rename a project across all surfaces (filesystem, GitHub, conda, files).",
)(rename)
