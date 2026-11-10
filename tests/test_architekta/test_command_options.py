"""
test_architekta.test_command_options
====================================

Tests for the options shared by the command lines of the workspace.

The commands take their project from ``--root``, else from ``ARCHITEKTA_ROOT``, else from the
current folder. The former names of renamed options are rejected. The options of ``rename`` work
in any position, and an unknown trailing token is a usage error. A rename asks for a confirmation,
which ``--yes`` answers, and stops without a terminal and without ``--yes``.

See Also
--------
architekta.rename.commands, architekta.env.commands
    Tested modules.
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
        return SimpleNamespace(stages=(), succeeded=True)

    monkeypatch.delenv("ARCHITEKTA_ROOT", raising=False)
    monkeypatch.setattr("architekta.rename.commands.run_rename_pipeline", fake_pipeline)
    monkeypatch.setattr("architekta.rename.commands.parse_github_remote", lambda path: None)
    monkeypatch.setattr("architekta.rename.commands.render_dry_run", lambda report: "plan")
    monkeypatch.setattr("architekta.rename.commands._print_report", lambda report, verbose: None)
    return calls


@pytest.fixture
def install_requests(monkeypatch):
    """Replace the planning of an editable install by a recorder of its request."""
    requests = []

    def fake_plan(request):
        requests.append(request)
        return SimpleNamespace(plans=[])

    monkeypatch.delenv("ARCHITEKTA_ROOT", raising=False)
    monkeypatch.setattr("architekta.env.commands.plan_editable_install", fake_plan)
    monkeypatch.setattr("architekta.env.commands.get_site_packages", lambda: Path("/site-packages"))
    return requests


def _terminal(monkeypatch, is_terminal: bool) -> None:
    monkeypatch.setattr("architekta.rename.commands._stdin_is_terminal", lambda: is_terminal)


# --- rename: root and option names ----------------------------------------------------------------

def test_rename_takes_the_project_from_root(tmp_path, rename_calls):
    result = runner.invoke(app, ["rename", "-r", str(tmp_path),
                                 "--workspace-file", "old.code-workspace", "--dry-run", "old", "new"])
    assert result.exit_code == 0, result.output + result.stderr
    assert rename_calls[0]["project_path"] == tmp_path.resolve()
    assert rename_calls[0]["workspace"] == "old.code-workspace"


def test_rename_takes_the_project_from_the_environment(tmp_path, rename_calls, monkeypatch):
    monkeypatch.setenv("ARCHITEKTA_ROOT", str(tmp_path))
    result = runner.invoke(app, ["rename", "old", "new", "--dry-run"])
    assert result.exit_code == 0, result.output + result.stderr
    assert rename_calls[0]["project_path"] == tmp_path.resolve()


@pytest.mark.parametrize("former", [["--path", "."], ["--workspace", "old.code-workspace"]])
def test_rename_rejects_the_former_option_names(former, rename_calls):
    result = runner.invoke(app, ["rename", "old", "new", "--dry-run", *former])
    assert result.exit_code == 2
    assert rename_calls == []


def test_rename_help_lists_only_the_current_names():
    help_text = runner.invoke(app, ["rename", "--help"]).stdout
    assert "--root" in help_text and "--workspace-file" in help_text and "--yes" in help_text
    assert "--path" not in help_text
    assert "--workspace " not in help_text


# --- rename: position of the options --------------------------------------------------------------

def test_rename_reads_options_written_after_the_names(tmp_path, rename_calls):
    result = runner.invoke(app, ["rename", "old", "new", "--dry-run", "--root", str(tmp_path),
                                 "--alias", "older"])
    assert result.exit_code == 0, result.output + result.stderr
    assert rename_calls[0]["dry_run"] is True
    assert rename_calls[0]["project_path"] == tmp_path.resolve()
    assert rename_calls[0]["aliases"] == ("older",)


def test_rename_reads_options_written_between_the_names(tmp_path, rename_calls):
    result = runner.invoke(app, ["rename", "old", "--dry-run", "new"])
    assert result.exit_code == 0, result.output + result.stderr
    assert rename_calls[0]["old_name"] == "old" and rename_calls[0]["new_name"] == "new"


def test_rename_rejects_an_unknown_trailing_token(rename_calls):
    result = runner.invoke(app, ["rename", "old", "new", "--dry-run", "extra"])
    assert result.exit_code == 2
    assert rename_calls == []


def test_rename_rejects_missing_names(rename_calls):
    result = runner.invoke(app, ["rename", "old"])
    assert result.exit_code == 2
    assert rename_calls == []


# --- rename: confirmation -------------------------------------------------------------------------

def test_rename_stops_without_a_terminal_and_without_yes(tmp_path, rename_calls, monkeypatch):
    _terminal(monkeypatch, False)
    result = runner.invoke(app, ["rename", "old", "new", "--root", str(tmp_path)])
    assert result.exit_code == 2
    assert "--yes" in result.stderr
    assert rename_calls == []


def test_rename_runs_without_a_terminal_with_yes(tmp_path, rename_calls, monkeypatch):
    _terminal(monkeypatch, False)
    result = runner.invoke(app, ["rename", "old", "new", "--root", str(tmp_path), "--yes"])
    assert result.exit_code == 0, result.output + result.stderr
    assert rename_calls[0]["dry_run"] is False


def test_rename_asks_on_a_terminal(tmp_path, rename_calls, monkeypatch):
    _terminal(monkeypatch, True)
    declined = runner.invoke(app, ["rename", "old", "new", "--root", str(tmp_path)], input="n\n")
    assert declined.exit_code == 1
    assert rename_calls == []
    accepted = runner.invoke(app, ["rename", "old", "new", "--root", str(tmp_path)], input="y\n")
    assert accepted.exit_code == 0, accepted.output + accepted.stderr
    assert len(rename_calls) == 1


def test_rename_dry_run_needs_no_confirmation(tmp_path, rename_calls, monkeypatch):
    _terminal(monkeypatch, False)
    result = runner.invoke(app, ["rename", "old", "new", "--root", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0, result.output + result.stderr


# --- env install-editable: root and --package-dir -------------------------------------------------

def test_install_editable_takes_the_project_from_root(tmp_path, install_requests):
    result = runner.invoke(app, ["env", "install-editable", "--all", "-r", str(tmp_path),
                                 "--dry-run"])
    assert result.exit_code == 0, result.output + result.stderr
    assert install_requests[0].workspace_root == tmp_path.resolve()


def test_install_editable_takes_the_project_from_the_environment(tmp_path, install_requests,
                                                                 monkeypatch):
    monkeypatch.setenv("ARCHITEKTA_ROOT", str(tmp_path))
    result = runner.invoke(app, ["env", "install-editable", "--all", "--dry-run"])
    assert result.exit_code == 0, result.output + result.stderr
    assert install_requests[0].workspace_root == tmp_path.resolve()


def test_install_editable_reads_package_dir_from_the_current_folder(tmp_path, install_requests,
                                                                    monkeypatch):
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["env", "install-editable", "--root", str(project),
                                 "--package-dir", "libs/alpha", "--dry-run"])
    assert result.exit_code == 0, result.output + result.stderr
    assert install_requests[0].custom_path == tmp_path.resolve() / "libs" / "alpha"


def test_install_editable_rejects_the_former_path_option(tmp_path, install_requests):
    result = runner.invoke(app, ["env", "install-editable", "--path", str(tmp_path), "--dry-run"])
    assert result.exit_code == 2
    assert install_requests == []


def test_install_editable_refuses_a_different_pth_without_force(tmp_path, monkeypatch):
    project = tmp_path / "project"
    (project / "src" / "alpha").mkdir(parents=True)
    (project / "src" / "alpha" / "__init__.py").write_text("")
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    pth = site_packages / "alpha.pth"
    monkeypatch.delenv("ARCHITEKTA_ROOT", raising=False)
    monkeypatch.setenv("CONDA_PREFIX", str(tmp_path / "envs" / "work"))
    monkeypatch.setattr("architekta.env.commands.get_site_packages", lambda: site_packages)

    pth.write_text("/elsewhere")
    refused = runner.invoke(app, ["env", "install-editable", "alpha", "--root", str(project)])
    assert refused.exit_code == 2
    assert str(pth) in refused.stderr
    assert pth.read_text() == "/elsewhere"

    forced = runner.invoke(app, ["env", "install-editable", "alpha", "--root", str(project),
                                 "--force"])
    assert forced.exit_code == 0, forced.output + forced.stderr
    assert pth.read_text() == str((project / "src" / "alpha").resolve())

    again = runner.invoke(app, ["env", "install-editable", "alpha", "--root", str(project)])
    assert again.exit_code == 0, again.output + again.stderr
