"""
architekta.cli
==============

Command-line interface for the architekta package.

Commands
--------
Commands are organized hierarchically into groups (sub-commands) corresponding to specific project
tasks:

Warning
-------
The logical groups do not directly correspond to the modules in which the commands are defined.
Rather, groups are composed by combining commands from different modules. Modules are organized by
tool (e.g. `env` for conda, `repo` for git and GitHub, etc.) rather than by high-level task (e.g.
setup, inspect, etc.). Each high-level task may involve multiple tools (e.g. setup env, setup repo,
etc.).


See Also
--------
typer : https://typer.tiangolo.com/
    Library for building CLI applications.
"""

import typer

# from architekta.commands.env import app as env_app

# Main Typer app
app = typer.Typer(no_args_is_help=True)  # no arg -> show help

# Command groups
inspect_app = typer.Typer()
app.add_typer(inspect_app, name="inspect", help="Inspect project's state.")

setup_app = typer.Typer()
app.add_typer(setup_app, name="setup", help="Setup project components, structure and configurations.")

update_app = typer.Typer()
app.add_typer(update_app, name="update", help="Update project components, structure and configurations.")

run_app = typer.Typer()
app.add_typer(run_app, name="run", help="Run code analysis for quality, tests, and documentation.")

version_app = typer.Typer()
app.add_typer(version_app, name="version", help="Manage versioning and releases.")

dist_app = typer.Typer()
app.add_typer(dist_app, name="dist", help="Manage project distribution.")


if __name__ == "__main__":
    app()
