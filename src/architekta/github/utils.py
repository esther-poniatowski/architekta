"""Utility functions for GitHub repository metadata operations."""

from pathlib import Path

import tomlkit
from tomlkit.exceptions import TOMLKitError

from architekta.github.exceptions import (
    DescriptionNotFound,
    GhCliError,
    GitHubError,
    MetadataParseError,
    RemoteNotFound,
)
from architekta.infrastructure import GithubSlug, parse_github_remote, run_command


def extract_readme_description(project_dir: Path) -> str:
    """Extract the first descriptive sentence from a project README.

    Skips the title heading, badge lines, horizontal rules, HTML comments,
    and blank lines, returning the first line of plain prose.
    """
    readme = project_dir / "README.md"
    if not readme.exists():
        raise DescriptionNotFound(f"No README.md in {project_dir}")
    in_comment = False
    for line in readme.read_text().splitlines():
        stripped = line.strip()
        if "<!--" in stripped:
            in_comment = True
        if in_comment:
            if "-->" in stripped:
                in_comment = False
            continue
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("[!["):
            continue
        if stripped == "---":
            continue
        return stripped
    raise DescriptionNotFound(f"No description found in {readme}")


def _run_checked(args: list[str], error_cls: type[GitHubError], context: str) -> str:
    result = run_command(args)
    if not result.ok:
        detail = result.stderr or result.stdout or "command failed"
        raise error_cls(f"{context}: {detail}", diagnostics=result)
    return result.stdout


def get_github_remote(project_dir: Path) -> GithubSlug:
    """Parse the origin remote URL to extract the GitHub owner and repo.

    Returns a ``GithubSlug`` with ``owner`` and ``repo`` fields.

    Raises
    ------
    RemoteNotFound
        If the git remote cannot be read or the URL is not a GitHub URL.
    """
    slug = parse_github_remote(project_dir)
    if slug is None:
        raise RemoteNotFound(
            f"Cannot detect GitHub owner/repo from git remote in {project_dir}"
        )
    return slug


def get_current_description(owner: str, repo: str) -> str:
    """Fetch the current GitHub repository description via the gh CLI."""
    return _run_checked(
        ["gh", "repo", "view", f"{owner}/{repo}", "--json", "description", "-q", ".description"],
        error_cls=GhCliError,
        context=f"Failed to query {owner}/{repo}",
    )


def set_description(owner: str, repo: str, description: str) -> None:
    """Update the GitHub repository description via the gh CLI."""
    _run_checked(
        ["gh", "repo", "edit", f"{owner}/{repo}", "--description", description],
        error_cls=GhCliError,
        context=f"Failed to update {owner}/{repo}",
    )


def get_pyproject_description(project_dir: Path) -> str | None:
    """Read the description field from pyproject.toml, or None if absent."""
    pyproject = project_dir / "pyproject.toml"
    if not pyproject.exists():
        return None
    try:
        doc = tomlkit.parse(pyproject.read_text())
    except (OSError, TOMLKitError) as exc:
        raise MetadataParseError(f"Failed to parse {pyproject}: {exc}") from exc
    project_table = doc.get("project")
    if not project_table or "description" not in project_table:
        return None
    return str(project_table["description"]).strip()


def set_pyproject_description(project_dir: Path, description: str) -> None:
    """Update the description field in pyproject.toml in place."""
    pyproject = project_dir / "pyproject.toml"
    try:
        text = pyproject.read_text()
        doc = tomlkit.parse(text)
    except (OSError, TOMLKitError) as exc:
        raise MetadataParseError(f"Failed to parse {pyproject}: {exc}") from exc
    project_table = doc.get("project")
    if not project_table or "description" not in project_table:
        raise DescriptionNotFound(f"No description field in {pyproject}")
    project_table["description"] = description
    try:
        pyproject.write_text(tomlkit.dumps(doc))
    except OSError as exc:
        raise MetadataParseError(f"Failed to write {pyproject}: {exc}") from exc
