"""Pure domain operations for GitHub synchronization."""

from dataclasses import dataclass
from pathlib import Path

from architekta.github.exceptions import GitHubError
from architekta.github.utils import (
    extract_readme_description,
    get_github_remote,
    get_current_description,
    get_pyproject_description,
)


@dataclass(frozen=True)
class SyncTarget:
    """A single project's sync status for one target (github or pyproject)."""
    project_name: str
    target: str  # "github" or "pyproject"
    current: str | None
    desired: str
    in_sync: bool
    error: str | None = None


def discover_sibling_projects(cwd: Path) -> list[Path]:
    """Return sibling directories of ``cwd`` that contain a README.md."""
    parent = cwd.parent
    return [
        d
        for d in parent.iterdir()
        if d.is_dir() and d != cwd and (d / "README.md").exists() and (d / ".git").is_dir()
    ]


def sync_descriptions(dirs: list[Path]) -> list[SyncTarget]:
    """Analyze sync status for all projects without performing writes."""
    targets = []
    for project_dir in sorted(dirs):
        name = project_dir.name

        try:
            readme_desc = extract_readme_description(project_dir)
        except GitHubError as exc:
            targets.append(SyncTarget(name, "readme", None, "", False, error=str(exc)))
            continue

        # GitHub target
        try:
            owner, repo = get_github_remote(project_dir)
            current_gh = get_current_description(owner, repo)
            targets.append(SyncTarget(name, "github", current_gh, readme_desc, current_gh == readme_desc))
        except GitHubError as exc:
            targets.append(SyncTarget(name, "github", None, readme_desc, False, error=str(exc)))

        # pyproject.toml target
        current_pp = get_pyproject_description(project_dir)
        if current_pp is None:
            targets.append(SyncTarget(name, "pyproject", None, readme_desc, False, error="no pyproject.toml or no description field"))
        else:
            targets.append(SyncTarget(name, "pyproject", current_pp, readme_desc, current_pp == readme_desc))

    return targets
