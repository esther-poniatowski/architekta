"""
test_architekta.test_cli
========================

Tests for the foundations of the CLI.

This test suite ensures that the CLI:

- Defines the main CLI entry point (architekta).
- Supports basic execution (architekta --help).
- Contains high-level command groups (although they might be empty).
- Handles unknown commands gracefully.

See Also
--------
architekta.cli
    Tested module.
typer.testing.CliRunner
    Class for testing Typer applications.
"""
import pytest
import typer
from typer.testing import CliRunner

from architekta.cli import app # main app

runner = CliRunner() # Typer testing runner

# --- Fixtures -------------------------------------------------------------------------------------

@pytest.fixture
def cli_groups():
    """
    Fixture defining the high-level command groups expected in the application.

    Returns
    -------
    set
       Names of the high-level command groups.
    """
    return {"setup", "update", "inspect", "run", "version", "dist"}

# --- Tests ----------------------------------------------------------------------------------------

def test_cli_invocation():
    """Test that the CLI can be invoked with no argument."""
    result = runner.invoke(app)
    assert result.exit_code == 0

def test_cli_help():
    """
    Test that the CLI displays help information.

    Notes
    -----
    The help command should be automatically provided by Typer.
    """
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

def test_unknown_command():
    """Ensure unknown commands return an error message."""
    result = runner.invoke(app, ["unknown-command"])
    assert result.exit_code != 0

def test_cli_groups_registered(cli_groups):
    """Ensure high-level command groups are attached to the main application."""
    registered_groups = {cmd.name for cmd in app.registered_groups if cmd.name}
    for group in cli_groups:
        assert group in registered_groups, f"Command group '{group}' not registered in main app: {registered_groups}"

def test_cli_groups_documented(cli_groups):
    """Ensure high-level command groups are documented in the help output."""
    result = runner.invoke(app, ["--help"])
    for group in cli_groups:
        assert group in result.output, f"Command group '{group}' missing from help output"
