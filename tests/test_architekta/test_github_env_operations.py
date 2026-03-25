from pathlib import Path

from architekta.env.operations import EditableInstallRequest, plan_editable_install
from architekta.github.operations import sync_descriptions


def test_sync_descriptions_dry_run_uses_service_boundary(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()

    monkeypatch.setattr(
        "architekta.github.operations.extract_readme_description",
        lambda project_dir: "Desired description",
    )
    monkeypatch.setattr(
        "architekta.github.operations._read_github_description",
        lambda project_dir: "Old GitHub description",
    )
    monkeypatch.setattr(
        "architekta.github.operations.get_pyproject_description",
        lambda project_dir: "Old pyproject description",
    )

    writes: list[tuple[str, str]] = []
    monkeypatch.setattr(
        "architekta.github.operations._write_github_description",
        lambda project_dir, description: writes.append(("github", description)),
    )
    monkeypatch.setattr(
        "architekta.github.operations.set_pyproject_description",
        lambda project_dir, description: writes.append(("pyproject", description)),
    )

    result = sync_descriptions([project], dry_run=True)

    assert writes == []
    assert [target.outcome for target in result.targets] == ["dry-run", "dry-run"]
    assert [target.target for target in result.targets] == ["github", "pyproject"]
    assert result.has_failures is False


def test_sync_descriptions_applies_updates(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()

    monkeypatch.setattr(
        "architekta.github.operations.extract_readme_description",
        lambda project_dir: "Desired description",
    )
    monkeypatch.setattr(
        "architekta.github.operations._read_github_description",
        lambda project_dir: "Old GitHub description",
    )
    monkeypatch.setattr(
        "architekta.github.operations.get_pyproject_description",
        lambda project_dir: "Old pyproject description",
    )

    writes: list[tuple[str, str]] = []
    monkeypatch.setattr(
        "architekta.github.operations._write_github_description",
        lambda project_dir, description: writes.append(("github", description)),
    )
    monkeypatch.setattr(
        "architekta.github.operations.set_pyproject_description",
        lambda project_dir, description: writes.append(("pyproject", description)),
    )

    result = sync_descriptions([project], dry_run=False)

    assert writes == [("github", "Desired description"), ("pyproject", "Desired description")]
    assert [target.outcome for target in result.targets] == ["updated", "updated"]


def test_plan_editable_install_uses_explicit_workspace_root(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    package_dir = workspace / "src" / "alpha"
    tests_dir = workspace / "src" / "tests"
    site_packages = tmp_path / "site-packages"
    package_dir.mkdir(parents=True)
    tests_dir.mkdir(parents=True)
    site_packages.mkdir()
    (package_dir / "__init__.py").write_text("")

    request = EditableInstallRequest(
        workspace_root=workspace,
        site_packages=site_packages,
        package_names=("alpha",),
        include_tests=True,
    )

    result = plan_editable_install(request)

    assert result.site_packages == site_packages
    assert isinstance(result.plans, tuple)
    assert result.plans[0].package.name == "alpha"
    assert result.plans[0].pth_file == site_packages / "alpha.pth"
    assert result.plans[0].lines == (
        str(package_dir.resolve()),
        str(tests_dir.resolve()),
    )


def test_plan_editable_install_marks_existing_pth_as_skipped(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    package_dir = workspace / "src" / "alpha"
    site_packages = tmp_path / "site-packages"
    package_dir.mkdir(parents=True)
    site_packages.mkdir()
    (package_dir / "__init__.py").write_text("")
    (site_packages / "alpha.pth").write_text("existing")

    request = EditableInstallRequest(
        workspace_root=workspace,
        site_packages=site_packages,
        package_names=("alpha",),
        force=False,
    )

    result = plan_editable_install(request)

    assert result.plans[0].skipped is True
    assert "use --force to overwrite" in result.plans[0].skip_reason
