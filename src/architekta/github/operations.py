"""Pure domain operations for GitHub synchronization."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

from architekta.github.exceptions import GitHubError
from architekta.github.utils import (
    extract_readme_description,
    get_github_remote,
    get_current_description,
    set_description,
    get_pyproject_description,
    set_pyproject_description,
)


@dataclass(frozen=True)
class SyncTargetResult:
    """Outcome for synchronizing one metadata target of one project."""

    project_name: str
    target: str
    current: str | None
    desired: str | None
    outcome: Literal["ok", "dry-run", "updated", "skipped", "error"]
    message: str
    failed: bool = False


@dataclass(frozen=True)
class SyncBatchResult:
    """Result of a batch metadata synchronization."""

    targets: tuple[SyncTargetResult, ...]

    @property
    def has_failures(self) -> bool:
        return any(target.failed for target in self.targets)


@dataclass(frozen=True)
class TargetBinding:
    """Read and write behavior for one sync target."""

    name: str
    read_current: Callable[[Path], str | None]
    apply: Callable[[Path, str], None]
    missing_message: str | None = None


def discover_sibling_projects(cwd: Path) -> list[Path]:
    """Return sibling directories of ``cwd`` that contain a README.md."""
    parent = cwd.parent
    return [
        d
        for d in parent.iterdir()
        if d.is_dir() and d != cwd and (d / "README.md").exists() and (d / ".git").is_dir()
    ]


def sync_descriptions(dirs: list[Path], *, dry_run: bool = False) -> SyncBatchResult:
    """Synchronize project descriptions across configured metadata targets."""
    targets: list[SyncTargetResult] = []
    bindings = (
        TargetBinding("github", _read_github_description, _write_github_description),
        TargetBinding(
            "pyproject",
            get_pyproject_description,
            set_pyproject_description,
            missing_message="no pyproject.toml or no description field",
        ),
    )
    for project_dir in sorted(dirs):
        name = project_dir.name

        try:
            readme_desc = extract_readme_description(project_dir)
        except GitHubError as exc:
            targets.append(
                SyncTargetResult(
                    project_name=name,
                    target="readme",
                    current=None,
                    desired=None,
                    outcome="skipped",
                    message=str(exc),
                    failed=True,
                )
            )
            continue

        for binding in bindings:
            targets.append(_sync_target(project_dir, name, readme_desc, binding, dry_run=dry_run))

    return SyncBatchResult(targets=tuple(targets))


def _sync_target(
    project_dir: Path,
    project_name: str,
    desired: str,
    binding: TargetBinding,
    *,
    dry_run: bool,
) -> SyncTargetResult:
    try:
        current = binding.read_current(project_dir)
    except GitHubError as exc:
        return SyncTargetResult(
            project_name=project_name,
            target=binding.name,
            current=None,
            desired=desired,
            outcome="skipped",
            message=str(exc),
            failed=True,
        )

    if current is None:
        return SyncTargetResult(
            project_name=project_name,
            target=binding.name,
            current=None,
            desired=desired,
            outcome="skipped",
            message=binding.missing_message or "target unavailable",
        )

    if current == desired:
        return SyncTargetResult(
            project_name=project_name,
            target=binding.name,
            current=current,
            desired=desired,
            outcome="ok",
            message="already in sync",
        )

    if dry_run:
        return SyncTargetResult(
            project_name=project_name,
            target=binding.name,
            current=current,
            desired=desired,
            outcome="dry-run",
            message=f"\"{current}\" -> \"{desired}\"",
        )

    try:
        binding.apply(project_dir, desired)
    except GitHubError as exc:
        return SyncTargetResult(
            project_name=project_name,
            target=binding.name,
            current=current,
            desired=desired,
            outcome="error",
            message=str(exc),
            failed=True,
        )

    return SyncTargetResult(
        project_name=project_name,
        target=binding.name,
        current=current,
        desired=desired,
        outcome="updated",
        message=f"\"{desired}\"",
    )


def _read_github_description(project_dir: Path) -> str:
    owner, repo = get_github_remote(project_dir)
    return get_current_description(owner, repo)


def _write_github_description(project_dir: Path, description: str) -> None:
    owner, repo = get_github_remote(project_dir)
    set_description(owner, repo, description)
