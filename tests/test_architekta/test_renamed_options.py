"""
test_architekta.test_renamed_options
====================================

Tests for the options renamed under the shared naming of command-line options.

Each renamed option must work under its current name, and under its former name with a warning on
the standard error, for one release. The former name stays out of the help output, and the two
names given together are rejected.

See Also
--------
architekta.renamed_options
    Tested module.
"""
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from architekta.cli import app

runner = CliRunner(mix_stderr=False)


# --- Fixtures -------------------------------------------------------------------------------------

@pytest.fixture
def rename_calls(monkeypatch):
    """Replace the rename pipeline by a recorder of its keyword arguments."""
    calls = []

    def fake_pipeline(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace()

    monkeypatch.setattr("architekta.rename.commands.run_rename_pipeline", fake_pipeline)
    monkeypatch.setattr("architekta.rename.commands.parse_github_remote", lambda path: None)
    monkeypatch.setattr("architekta.rename.commands.render_dry_run", lambda report: "plan")
    return calls


@pytest.fixture
def install_requests(monkeypatch):
    """Replace the planning of an editable install by a recorder of its request."""
    requests = []

    def fake_plan(request):
        requests.append(request)
        return SimpleNamespace(plans=[])

    monkeypatch.setattr("architekta.env.commands.plan_editable_install", fake_plan)
    monkeypatch.setattr("architekta.env.commands.get_site_packages", lambda: Path("/site-packages"))
    return requests


# --- rename: --root and --workspace-file ----------------------------------------------------------
# The options precede the names: `rename` is a group, which stops parsing options at its first
# positional argument.

def test_rename_takes_the_project_from_root(tmp_path, rename_calls):
    result = runner.invoke(app, ["rename", "--root", str(tmp_path),
                                 "--workspace-file", "old.code-workspace", "--dry-run", "old", "new"])
    assert result.exit_code == 0, result.output + result.stderr
    assert rename_calls[0]["project_path"] == tmp_path.resolve()
    assert rename_calls[0]["workspace"] == "old.code-workspace"
    assert "deprecated" not in result.stderr


def test_rename_accepts_the_former_names_with_a_warning(tmp_path, rename_calls):
    result = runner.invoke(app, ["rename", "--path", str(tmp_path),
                                 "--workspace", "old.code-workspace", "--dry-run", "old", "new"])
    assert result.exit_code == 0, result.output + result.stderr
    assert rename_calls[0]["project_path"] == tmp_path.resolve()
    assert rename_calls[0]["workspace"] == "old.code-workspace"
    assert "--path is deprecated" in result.stderr and "use --root" in result.stderr
    assert "--workspace is deprecated" in result.stderr and "use --workspace-file" in result.stderr


def test_rename_rejects_root_and_its_former_name_together(tmp_path, rename_calls):
    result = runner.invoke(app, ["rename", "--root", str(tmp_path),
                                 "--path", str(tmp_path), "--dry-run", "old", "new"])
    assert result.exit_code != 0
    assert rename_calls == []


def test_rename_help_lists_only_the_current_names():
    help_text = runner.invoke(app, ["rename", "--help"]).stdout
    assert "--root" in help_text and "--workspace-file" in help_text
    assert "--path" not in help_text
    assert "--workspace " not in help_text


# --- env install-editable: --package-dir ----------------------------------------------------------

def test_install_editable_takes_the_package_from_package_dir(tmp_path, install_requests):
    result = runner.invoke(app, ["env", "install-editable", "--package-dir", str(tmp_path),
                                 "--dry-run"])
    assert result.exit_code == 0, result.output + result.stderr
    assert install_requests[0].custom_path == tmp_path
    assert "deprecated" not in result.stderr


def test_install_editable_accepts_the_former_path_with_a_warning(tmp_path, install_requests):
    result = runner.invoke(app, ["env", "install-editable", "--path", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0, result.output + result.stderr
    assert install_requests[0].custom_path == tmp_path
    assert "--path is deprecated" in result.stderr and "use --package-dir" in result.stderr


def test_install_editable_help_lists_only_the_current_name():
    help_text = runner.invoke(app, ["env", "install-editable", "--help"]).stdout
    assert "--package-dir" in help_text
    assert "--path" not in help_text
