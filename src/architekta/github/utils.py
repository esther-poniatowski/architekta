"""Utility functions for GitHub repository metadata operations."""

import re
from pathlib import Path

import tomlkit

from architekta.github.exceptions import RemoteNotFound, DescriptionNotFound, GhCliError
from architekta.infrastructure import run_command


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


def get_github_remote(project_dir: Path) -> tuple[str, str]:
    """Parse the origin remote URL to extract the GitHub owner and repo name."""
    stdout = run_command(
        ["git", "-C", str(project_dir), "remote", "get-url", "origin"],
        error_cls=RemoteNotFound,
        context=f"No git remote 'origin' in {project_dir}",
    )
    match = re.search(r"github\.com[:/](.+?)/(.+?)(?:\.git)?$", stdout)
    if not match:
        raise RemoteNotFound(f"Cannot parse GitHub owner/repo from remote URL: {stdout}")
    return match.group(1), match.group(2)


def get_current_description(owner: str, repo: str) -> str:
    """Fetch the current GitHub repository description via the gh CLI."""
    return run_command(
        ["gh", "repo", "view", f"{owner}/{repo}", "--json", "description", "-q", ".description"],
        error_cls=GhCliError,
        context=f"Failed to query {owner}/{repo}",
    )


def set_description(owner: str, repo: str, description: str) -> None:
    """Update the GitHub repository description via the gh CLI."""
    run_command(
        ["gh", "repo", "edit", f"{owner}/{repo}", "--description", description],
        error_cls=GhCliError,
        context=f"Failed to update {owner}/{repo}",
    )


def get_pyproject_description(project_dir: Path) -> str | None:
    """Read the description field from pyproject.toml, or None if absent."""
    pyproject = project_dir / "pyproject.toml"
    if not pyproject.exists():
        return None
    doc = tomlkit.parse(pyproject.read_text())
    project_table = doc.get("project")
    if not project_table or "description" not in project_table:
        return None
    return str(project_table["description"]).strip()


def set_pyproject_description(project_dir: Path, description: str) -> None:
    """Update the description field in pyproject.toml in place."""
    pyproject = project_dir / "pyproject.toml"
    text = pyproject.read_text()
    doc = tomlkit.parse(text)
    project_table = doc.get("project")
    if not project_table or "description" not in project_table:
        raise DescriptionNotFound(f"No description field in {pyproject}")
    project_table["description"] = description
    pyproject.write_text(tomlkit.dumps(doc))
